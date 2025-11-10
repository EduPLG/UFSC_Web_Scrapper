from utils.get_csv import generate_df
from models.site import Site


if __name__ == "__main__":
    obj_ZapImoveis = Site.factory("ZapImoveis")
    obj_ZapImoveis.start_web_scrapping()  # city="florianopolis", aluguel=True

    obj_brognoli = Site.factory("Brognoli")
    obj_brognoli.start_web_scrapping()  # city="florianopolis", aluguel=True

    obj_ImoveisSC = Site.factory("Imoveis_SC")
    obj_ImoveisSC.start_web_scrapping()  # city="florianopolis", aluguel=True

    obj_AdrianoImoveis = Site.factory("AdrianoImoveis")
    obj_AdrianoImoveis.start_web_scrapping()

    # From output, get de first file

    df = generate_df()
    # Ao salvar, substitui os valores NaN pela string 'NULL' no arquivo CSV
    df.to_csv("output/data_base.csv", na_rep='NULL', index=False)
