from playwright.sync_api import sync_playwright
from playwright.sync_api import Page
from bs4 import BeautifulSoup
from tqdm import tqdm
from collections.abc import Callable
from utils.get_data_func import (
    save_elements_to_json
)


MAX_PAGE = 5


def get_page_content(url: str, next_page_func: Callable[[Page], bool]) -> list[BeautifulSoup]:
    """Obtém o conteúdo HTML de varias páginas usando Playwright."""
    SOUPS = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-position=-2000,-2000",  # joga fora da tela
                "--window-size=1,1"
            ]
        )
        page = browser.new_page(java_script_enabled=True)
        page.goto(url, wait_until="load", timeout=60000)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=- Next Page Loop -=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        print(f"Donwloading page ( 0 / {MAX_PAGE} )...", end="\r")
        for _ in range(1, MAX_PAGE + 1):
            content = page.content()
            page_soup = BeautifulSoup(content, "html.parser")
            if SOUPS:
                if page_soup == SOUPS[-1]:
                    print("Falha na troca de Página, verifique o site.\nFinalizando o download de páginas.")
                    break
            SOUPS.append(page_soup)  # Verifica se o HTML é válido
            if not next_page_func(page):
                break
            else:
                print(f"Donwloading page ( {_} / {MAX_PAGE} )...", end="\r")
        browser.close()
        return SOUPS


def save_site_content(url: str,
                      filter: tuple[str, dict],
                      get_imp_data_func: Callable[[BeautifulSoup], list[str]],
                      next_page_func: Callable[[Page], bool],
                      json_name: str) -> None:
    print(f"Acessando o site {url.split('.')[1]}...")
    soups = get_page_content(url, next_page_func)
    print("Páginas salvas com sucesso!")
    lista = []
    print("Extraindo os dados...")
    for pag_soup in tqdm(soups):
        elementos = pag_soup.find_all(filter[0], filter[1])
        lista += list(map(get_imp_data_func, elementos))
    print("Salvando os dados em JSON...")
    save_elements_to_json(lista, json_name)
    print(f"Dados salvos com sucesso! Verifique o arquivo {json_name}")
