import re
from playwright.sync_api import Page


def next_page_zapimoveis(page: Page) -> bool:
    btn = page.locator('button[data-testid="next-page"]')
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


def next_page_imoveisweb(page: Page) -> bool:
    old_url = page.url
    match = re.search(r'pagina-(\d+)\.html', old_url)

    if match:
        numero = int(match.group(1))  # pega o número como inteiro
        new_url = old_url.replace(f'pagina-{numero}.html', f'pagina-{numero + 1}.html')
    else:
        new_url = old_url.replace(".html", "") + '-pagina-2.html'
    try:
        page.goto(new_url, timeout=5000)
        page.wait_for_url(lambda url: url != old_url)
        page.wait_for_load_state("networkidle", timeout=1200000)
        return True
    except Exception as e:
        print(f"imoveisweb: erro ao tentar avançar -> {e}")
        return False


def next_page_brognoli(page: Page) -> bool:
    pagination = page.locator("ul.pagination")
    if not pagination.count():
        return False

    pagination.scroll_into_view_if_needed()

    # 1. Encontra o botão "active" atual
    active_locator = pagination.locator("a.active")
    if not active_locator.count():
        return False  # Não achou paginação ativa

    active_text = active_locator.text_content()

    try:
        # 2. Calcula o número da próxima página
        next_page_num = int(active_text) + 1
    except (ValueError, TypeError):
        print(f"brognoli: não foi possível ler o número da página ativa '{active_text}'")
        return False

    # 3. Encontra o botão da próxima página
    # Usamos :text-matches("^{next_page_num}$") para garantir uma correspondência exata
    # (ex: "3" e não "13")
    next_btn = pagination.locator(f'a:text-matches("^{next_page_num}$")')
    
    if not next_btn.count():
        return False  # Não há mais botões "próxima" (chegou ao fim)

    try:
        # 4. Clica no botão
        next_btn.click(timeout=5000)

        # 5. Espera até que a página mude

        # Este seletor só vai existir QUANDO a página nova carregar
        # e o "active" for atualizado para o 'next_page_num'
        new_active_locator = pagination.locator(f'a.active:text-matches("^{next_page_num}$")')
        
        # Espera até que o novo botão "active" esteja visível
        new_active_locator.wait_for(state="visible", timeout=15000)
        
        # BÔNUS: Adiciona uma espera por 'networkidle' para garantir que
        # os cards de imóveis também carregaram após a navegação.
        page.wait_for_load_state("load", timeout=10000)

        return True
    except Exception as e:
        # Se 'wait_for' der timeout, a página não mudou.
        print(f"brognoli: erro ao tentar avançar para a pág {next_page_num} -> {e}")
        return False
