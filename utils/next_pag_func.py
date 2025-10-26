from playwright.sync_api import Page


def next_page_zapimoveis(page: Page) -> bool:
    btn = page.locator('button[data-testid="next-page"]').first
    if not btn.count():
        return False  # Não há botão "próxima"

    if btn.get_attribute("disabled"):
        return False  # Botão "próxima" está desabilitado (última página)

    old_href = ""
    try:
        # --- ETAPA 1: Capturar o estado atual ---
        # Pegamos o seletor do seu arquivo get_imoveis.py
        first_item = page.locator('li[data-cy="rp-property-cd"]').first
        
        if first_item.count():
            # Tentar pegar o link 'href' do primeiro item como nosso "identificador"
            first_link = first_item.locator("a").first
            if first_link.count():
                old_href = first_link.get_attribute("href")
                
    except Exception as e:
        print(f"Zapimoveis: erro ao tentar ler o estado atual -> {e}")
        # Não é crítico, podemos tentar avançar mesmo assim

    try:
        # --- ETAPA 2: Clicar no botão ---
        btn.scroll_into_view_if_needed()
        btn.click(timeout=10000)

        # --- ETAPA 3: Esperar a mudança do conteúdo ---
        if old_href:
            # Esta função JS será executada no navegador.
            # Ela espera até que o 'href' do primeiro item seja DIFERENTE do antigo.
            js_function = f"""
            () => {{
                const firstLink = document.querySelector('li[data-cy="rp-property-cd"] a');
                if (!firstLink) return false; // Ainda não carregou
                
                const newHref = firstLink.getAttribute('href');
                return newHref !== '{old_href}'; // Retorna true quando o link for novo
            }}
            """
            # Espera até 15 segundos pela função se tornar verdadeira
            page.wait_for_function(js_function, timeout=15000)
        else:
            # Se falhamos em pegar o old_href, voltamos para a espera antiga,
            # mas usamos "load" que é mais rápido (embora menos confiável)
            page.wait_for_load_state("load", timeout=7000)

        return True
    except Exception as e:
        # Se o wait_for_function der timeout, significa que a página não mudou
        print(f"Zapimoveis: erro ao tentar avançar (timeout esperando conteúdo novo) -> {e}")
        return False


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
