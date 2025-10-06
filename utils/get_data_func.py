from pydantic import ValidationError
from bs4 import BeautifulSoup
from models.imovel import ImovelCard
import json
from os.path import join
from os import makedirs

PATH_OUTPUT = "output"


def save_elements_to_json(elements: list[dict], filename: str):
    """Salva uma lista de elementos em um arquivo JSON.

    Args:
        elements (list[dict]): Lista de elementos a serem salvos.
        filename (str): Nome do arquivo JSON onde os dados serão salvos.
    """
    if not filename.endswith(".json"):
        filename += ".json"

    makedirs(PATH_OUTPUT, exist_ok=True)

    with open(join(PATH_OUTPUT, filename), "w", encoding="utf-8") as file:
        json.dump(elements, file, ensure_ascii=False, indent=4)


def get_important_data_zapimoveis(imovel: BeautifulSoup):
    # Link do imóvel
    link = imovel.locator("a").get_attribute("href") or "None"

    # Título do imóvel
    title = imovel.locator("a").get_attribute("title") or ""

    # Localização (bairro/cidade)
    location = imovel.locator('[data-cy="rp-cardProperty-location-txt"]').text_content() or ""
    location = location.split("\n")[1] if "\n" in location else location

    # Endereço (rua)
    try:
        street = imovel.locator('[data-cy="rp-cardProperty-street-txt"]').text_content().strip()
    except:
        street = ""

    # Área
    try:
        area_txt = imovel.locator('[data-cy="rp-cardProperty-propertyArea-txt"]').text_content()
        area = float(area_txt.split("\n")[-1].replace("m²", "").replace(",", ".").strip())
    except:
        area = 0.0

    # Banheiros
    try:
        bathrooms_txt = imovel.locator('[data-cy="rp-cardProperty-bathroomQuantity-txt"]').text_content()
        bathrooms = int(bathrooms_txt.split("\n")[-1])
    except:
        bathrooms = 0

    # Quartos
    try:
        rooms_txt = imovel.locator('[data-cy="rp-cardProperty-bedroomQuantity-txt"]').text_content()
        rooms = int(rooms_txt.split("\n")[-1])
    except:
        rooms = 0

    # Preço
    try:
        price_txt = imovel.locator('[data-cy="rp-cardProperty-price-txt"] p').text_content()
    except:
        price_txt = None

    # Vagas
    try:
        parking_txt = imovel.locator('[data-cy="rp-cardProperty-parkingSpacesQuantity-txt"]').text_content()
        parking = int(parking_txt.split("\n")[-1])
    except:
        parking = 0

    try:
        object_imovel = ImovelCard(
            title=title,
            street=street,
            url=link,
            price_txt=price_txt,
            location=location,
            rooms=rooms,
            area=area,
            bathrooms=bathrooms,
            parking=parking
        )
    except ValidationError as e:
        print(e.errors())
        object_imovel = None
    return object_imovel.model_dump() if object_imovel else None


def get_important_data_imoveisweb(imovel: BeautifulSoup):
    pass

def get_important_data_brognoli(imovel: BeautifulSoup):
    # Título do imóvel
    try:
        title = imovel.find("a")["title"]
    except:
        print("Erro ao obter o título")
        title = "None"

    # Link do imóvel
    try:
        link = imovel.find("a")['href']
    except:
        print("Erro ao obter o link")
        link = "None"

    # Localização (bairro/cidade)
    try:
        location_full = imovel.find("span", {"class": "e"}).text.strip()
        if "," in location_full:
            street = location_full.split(",")[0].strip()
            location = location_full.split(",")[1].strip()
        else:
            street = location = location_full
    except:
        print("Erro ao obter a localização")
        location = street = "None"

    # Área, quartos, banheiros, vagas
    area = 0.0
    rooms = 0
    bathrooms = 0
    parking = 0
    try:
        features = imovel.find_all("li")
        for feature in features:
            text = feature.text.strip().lower()
            if 'm²' in text:
                area = float(text.replace('m²', '').strip())
            elif 'quartos' in text or 'dormitório' in text:
                rooms = int(text.split()[0])
            elif 'banheiro' in text:
                bathrooms = int(text.split()[0])
            else:
                try:
                    parking = int(text.strip())
                except:
                    parking = 0
    except:
        print("Erro ao obter área, quartos, banheiros ou vagas")
        area = 0.0
        rooms = 0
        bathrooms = 0
        parking = 0

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "v"}).text.strip()
    except:
        print("Erro ao obter o preço")
        price_txt = "0.0"

    try:
        object_imovel = ImovelCard(
            title=title,
            street=street,
            url=link,
            price_txt=price_txt,
            location=location,
            rooms=rooms,
            area=area,
            bathrooms=bathrooms,
            parking=parking
        )
    except ValidationError as e:
        print("ERROR: ", e.errors())
        object_imovel = None

    return object_imovel.model_dump_json() if object_imovel else None
