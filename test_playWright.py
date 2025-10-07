from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections.abc import Callable
from utils.get_data_func import (
    get_important_data_zapimoveis,
    get_important_data_brognoli,
    get_important_data_imoveisweb,
    save_elements_to_json
)


def get_page_content(url: str) -> list[BeautifulSoup]:
    """Obtém o conteúdo HTML de varias páginas usando Playwright."""
    SOUPS = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page(java_script_enabled=True)
        page.goto(url, wait_until="load", timeout=60000)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        content = page.content()
        page_soup = BeautifulSoup(content, "html.parser")
        SOUPS.append(page_soup)  # Verifica se o HTML é válido
        # TODO: Tenta ir para a próxima página
        browser.close()
        return SOUPS


def save_site_content(url: str,
                      filter: tuple[str, dict],
                      function: Callable[[BeautifulSoup], list[str]],
                      json_name: str) -> list[BeautifulSoup]:
    print("Acessando o site...")
    soups = get_page_content(url)
    print("Páginas salvas com sucesso!")
    lista = []
    print("Extraindo os dados...")
    for pag_soup in tqdm(soups):
        elementos = pag_soup.find_all(filter[0], filter[1])
        lista += list(map(function, elementos))
    print("Salvando os dados em JSON...")
    save_elements_to_json(lista, json_name)
    print(f"Dados salvos com sucesso! Verifique o arquivo {json_name}")


if __name__ == "__main__":
    save_site_content(
        "https://www.zapimoveis.com.br/aluguel",
        ("li", {"data-cy": "rp-property-cd"}),
        get_important_data_zapimoveis,
        "zapimoveis.json"
    )

    save_site_content(
        "https://www.imovelweb.com.br/imoveis-venda-santa-catarina.html",
        ("div", {"class": "postingsList-module__card-container"}),
        get_important_data_imoveisweb,
        "imovelweb.json"
    )
    
    save_site_content(
        "https://www.brognoli.com.br/comprar/cidade/biguacu/1",
        ("article", {"class": "imovel"}),
        get_important_data_brognoli,
        "brognoli.json")
