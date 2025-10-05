from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from utils.get_data_func import (
    get_important_data_zapimoveis,
    get_important_data_brognoli,
    save_elements_to_json
)


def get_page_content(url: str) -> list[BeautifulSoup]:
    """Obtém o conteúdo HTML de varias páginas usando Playwright."""
    SOUPS = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        page = browser.new_page(java_script_enabled=True)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        content = page.content()
        SOUPS.append(BeautifulSoup(content, "html.parser"))  # Verifica se o HTML é válido
        # TODO: Tenta ir para a próxima página
        browser.close()
        return SOUPS


def init_playwright_zapimoveis(url: str) -> None:
    soups = get_page_content(url)
    lista = []
    for pag_soup in soups:
        elementos = pag_soup.select('li[data-cy="rp-property-cd"]')
        print(elementos)
        lista += [get_important_data_zapimoveis(imovel) for imovel in elementos]
        # TODO: Tenta ir para a próxima página

    save_elements_to_json(lista, "zapimoveis.json")


def init_playwright_imoveisweb(url: str) -> None:
    soups = get_page_content(url)
    lista = []
    for pag_soup in soups:
        elementos = pag_soup.select('[data-cy="rp-property-cd"]')  # TROCAR
        lista += [get_important_data_zapimoveis(imovel) for imovel in elementos]  # TROCAR
        # TODO: Tenta ir para a próxima página
    
    save_elements_to_json(lista, "imoveisweb.json")


def init_playwright_brognoli(url: str) -> None:
    soups = get_page_content(url)
    lista = []
    for pag_soup in soups:
        elementos = pag_soup.select(".imovel")
        lista += [get_important_data_brognoli(imovel) for imovel in elementos]
        # TODO: Tenta ir para a próxima página

    save_elements_to_json(lista, "brognoli.json")


if __name__ == "__main__":
    # init_playwright_zapimoveis("https://www.zapimoveis.com.br/aluguel/")
    # init_playwright_imoveisweb("https://www.imovelweb.com.br/imoveis-venda-santa-catarina.html")
    init_playwright_brognoli("https://www.brognoli.com.br/comprar/cidade/biguacu/1")