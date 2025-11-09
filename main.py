from utils.get_data_func import get_elements_from_json
from models.site import Site
import os


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

    file_names = os.listdir("output")
    lista_de_imoveis = get_elements_from_json(file_names[0])

    # Agora você tem uma lista de objetos ImovelCard
    if lista_de_imoveis:
        primeiro_imovel = lista_de_imoveis[0]
        print(f"Título: {primeiro_imovel.title}")
        print(f"Preço (numérico): {primeiro_imovel.price_num}")
        print(f"URL: {primeiro_imovel.url}")
