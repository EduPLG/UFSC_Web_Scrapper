from playwright.sync_api import Page
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode


def next_page_imoveis_sc(page: Page) -> bool:
    paginacao_ul = page.locator('div.navigation')
    next_page_btn = paginacao_ul.locator("a.next").first

    if not next_page_btn.count():
        return False  # Não há mais botões "próxima" (chegou ao fim)

    try:
        page_ = next_page_btn.get_attribute("data-page")

        if not page_:
            print("Erro: Botão 'próxima' não tem o atributo 'data-page'.")
            return False
        page_ = int(page_) + 1
        next_page_btn.scroll_into_view_if_needed()
        next_page_btn.click(timeout=5000)
        # Espera até que a página mude
        new_active_locator = paginacao_ul.locator(f'a.next[data-page="{page_}"]').first
        # Espera até que o novo botão "active" esteja visível
        new_active_locator.wait_for(state="visible", timeout=15000)

        # BÔNUS: Adiciona uma espera por 'networkidle' para garantir que
        # os cards de imóveis também carregaram após a navegação.
        page.wait_for_load_state("load", timeout=10000)
        return True
    except Exception as e:
        print(f"creditoreal: erro ao tentar avançar -> {e}")
        return False


def next_page_brognoli(page: Page) -> bool:
    pagination = page.locator("ul.pagination")
    if not pagination.count():
        return False

    pagination.scroll_into_view_if_needed()

    active_locator = pagination.locator("a.active").first
    if not active_locator.count():
        return False  # Não achou paginação ativa

    active_text = active_locator.text_content()

    try:
        next_page_num = int(active_text) + 1
    except (ValueError, TypeError):
        print(f"brognoli: não foi possível ler o número da página ativa '{active_text}'")
        return False

    next_btn = pagination.locator(f'a:text-matches("^{next_page_num}$")')

    if not next_btn.count():
        return False  # Não há mais botões "próxima" (chegou ao fim)

    try:
        next_btn.click(timeout=5000)

        # Este seletor só vai existir QUANDO a página nova carregar
        new_active_locator = pagination.locator(f'a.active:text-matches("^{next_page_num}$")')

        # Espera até que o novo botão "active" esteja visível
        new_active_locator.wait_for(state="visible", timeout=15000)

        page.wait_for_load_state("load", timeout=10000)

        return True
    except Exception as e:
        # Se 'wait_for' der timeout, a página não mudou.
        print(f"brognoli: erro ao tentar avançar para a pág {next_page_num} -> {e}")
        return False


def next_page_adrianoimoveis(page: Page) -> bool:
    try:
        cur_url = page.url
        parts = urlsplit(cur_url)
        qs = parse_qs(parts.query)

        try:
            cur_page = int(qs.get("page", ["1"])[0])
        except Exception:
            cur_page = 1

        next_page = cur_page + 1
        qs["page"] = [str(next_page)]

        next_query = urlencode(qs, doseq=True)
        next_url = urlunsplit((parts.scheme, parts.netloc, parts.path, next_query, parts.fragment))

        page.goto(next_url, wait_until="domcontentloaded", timeout=15000)

        # checa se tem cards de imóvel
        try:
            page.wait_for_selector('a[href^="/imovel/"]', timeout=5000)
        except Exception:
            return False

        if page.url == cur_url:
            return False

        return True

    except Exception as e:
        print(f"adrianoimoveis: erro ao tentar avançar -> {e}")
        return False
