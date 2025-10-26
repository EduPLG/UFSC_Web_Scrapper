from models.site import Site


if __name__ == "__main__":
    obj_ZapImoveis = Site.factory("ZapImoveis")
    obj_ZapImoveis.start_web_scrapping()  # city="florianopolis", aluguel=True

    obj_brognoli = Site.factory("Brognoli")
    obj_brognoli.start_web_scrapping()  # city="florianopolis", aluguel=True

    obj_ImoveisSC = Site.factory("Imoveis_SC")
    obj_ImoveisSC.start_web_scrapping()  # city="florianopolis", aluguel=True
