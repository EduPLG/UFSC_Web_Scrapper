from urllib.parse import urljoin
from typing import List
from playwright.sync_api import sync_playwright
from models.imovel import ImovelCard
from utils import to_float, to_int


ICON_PREFIX = {
    "M0 176c0-26.5": "area_m2",      # ícone da metragem
    "M176 288c44.1": "quartos",      # ícone dos quartos
    "m20.772 10.155": "vagas",       # ícone das vagas
    "M288 384c-17.67": "banheiros",  # ícone dos banheiros
}

def main():
    page = 1
    url = f"https://www.brognoli.com.br/comprar/cidade/florianopolis/bairros/abraao_acores_agronomica_alto-ribeirao_alto-ribeirao-leste_armacao_armacao-do-pantano-do-sul_autodromo_balneario_barra-da-lagoa_barra-do-sambaqui_beira-mar_beiramar_bom-abrigo_cachoeira-do-bom-jesus_cachoeira-do-bom-jesus-leste_cacupe_caiacanga_caieira_campeche_campeche-central_campeche-ii_campeche-leste_campeche-norte_campeche-sul_canasvieiras_canto_canto-da-lagoa_canto-dos-aracas_capoeiras_carianos_carvoeira_centro_coloninha_coqueiros_corrego-grande_costeira-do-pirajubae_costeira-do-ribeirao_daniela_estreito_estreto_ingleses_ingleses-do-rio-vermelho_itacorubi_itacurubi_itaguacu_jardim-anchieta_jardim-atlantico_jardim-nova-cachoeira_joao-paulo_jose-mendes_jurere_jurere-internacional_jurere-leste_jurere-oeste_lagoa-da-conceicao_lagoa-do-peri_lagoa-pequena_lagoinha_lagoinha-do-norte_moenda_monte-verde_morro-da-cruz_morro-das-pedras_morro-do-matadeiro_novo-campeche_pantanal_pantano-do-sul_parque-sao-jorge_pedregal_ponta-das-canas_portal-do-ribeirao_porto-da-lagoa_praia-brava_praia-mole_ratones_recanto-dos-acores_ressacada_retiro_ribeirao-da-ilha_rio-das-pacas_rio-tavares_rio-tavares-central_rio-tavares-do-norte_rio-vermelho_saco-dos-limoes_saco-grande_sambaqui_santa-monica_santinho_santo-antonio-de-lisboa_sao-joao-do-rio-vermelho_tapera_tapera-da-base_trindade_vargem-do-bom-jesus_vargem-grande_vargem-pequena/categoria/apartamentos/{page}/"
    imovel_list: List[ImovelCard] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        list_page = browser.new_page()
        list_page.goto(url, wait_until="domcontentloaded", timeout=60000)

        resultados = list_page.locator("#resultados")
        imoveis = resultados.locator(".imovel")
        total = imoveis.count()

        links: List[str] = []
        if total > 0:
            for i in range(total):
                href = imoveis.nth(i).locator("a.i").get_attribute("href")
                if href:
                    links.append(urljoin(url, href))

        for link in links:
            detail = browser.new_page()
            detail.goto(link, wait_until="domcontentloaded", timeout=60000)

            title = detail.title()
            valor_texto = detail.locator(".form-sidebar .valor .va").text_content().strip()

            specs = {"area_m2": None, "quartos": None, "vagas": None, "banheiros": None}
            items = detail.locator("ul.its > li")
            n = items.count()
            for i in range(n):
                li = items.nth(i)
                d_attr = li.locator("svg path").first.get_attribute("d") or ""
                span_txt = (li.locator("span").first.text_content() or "").strip()

                tipo = None
                for pref, campo in ICON_PREFIX.items():
                    if d_attr.startswith(pref):
                        tipo = campo
                        break
                if not tipo:

                    continue

                if tipo == "area_m2":
                    specs[tipo] = to_float(span_txt)
                else:
                    specs[tipo] = to_int(span_txt)

            imovel = ImovelCard(
                url=link,
                titulo=title,
                valor_texto=valor_texto,
                area=specs["area_m2"],
                quartos=specs["quartos"],
                vagas=specs["vagas"],
                banheiros=specs["banheiros"]
            )

            imovel_list.append(imovel)

            detail.close()

        for imovel in imovel_list:
            print(imovel.model_dump_json())

        list_page.close()
        browser.close()

    print("Finalizado!")

if __name__ == "__main__":
    main()
