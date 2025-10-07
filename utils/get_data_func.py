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
    try:
        link = imovel.find("a")["href"]
    except Exception as e:
        link = "None"
        
    # Título do imóvel
    try:
        title = imovel.find("a")["title"]
    except Exception as e:
        title = "None"
    try:
        # Localização (bairro/cidade)
        location = imovel.find("h2", {"data-cy": "rp-cardProperty-location-txt"}).text or ""
        location = location.split("\n")[1] if "\n" in location else location
    except Exception as e:
        location = ""
        
    # Endereço (rua)
    try:
        street = imovel.find("p", {"data-cy": "rp-cardProperty-street-txt"}).text.strip()
    except Exception as e:
        street = ""

    # Área
    try:
        area_txt = imovel.find("li", {"data-cy": "rp-cardProperty-propertyArea-txt"}).text
        area = float(area_txt.split("\n")[-1].replace("m²", "").replace(",", ".").strip())
    except Exception as e:
        area = 0.0

    # Banheiros
    try:
        bathrooms_txt = imovel.find("li", {"data-cy": "rp-cardProperty-bathroomQuantity-txt"}).text
        bathrooms = int(bathrooms_txt.split("\n")[-1])
    except Exception as e:
        bathrooms = 0

    # Quartos
    try:
        rooms_txt = imovel.find("li", {"data-cy": "rp-cardProperty-bedroomQuantity-txt"}).text
        rooms = int(rooms_txt.split("\n")[-1])
    except Exception as e:
        rooms = 0

    # Preço
    try:
        price_txt = imovel.find("div", {"data-cy": "rp-cardProperty-price-txt"}).text
    except Exception as e:
        price_txt = None

    # Vagas
    try:
        parking_txt = imovel.find("li", {"data-cy": "rp-cardProperty-parkingSpacesQuantity-txt"}).text
        parking = int(parking_txt.split("\n")[-1])
    except Exception as e:
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
        return None
    return object_imovel.model_dump_json()


def get_important_data_imoveisweb(imovel: BeautifulSoup):
    # Título do imóvel
    try:
        title = imovel.find("h3", {"data-qa": "POSTING_CARD_DESCRIPTION"}).text
    except Exception as e:
        title = "None"

    # Link do imóvel
    try:
        link = imovel.find('a')["href"]
        if not link.startswith("http"):
            link = "https://www.imovelweb.com.br" + link
    except Exception as e:
        link = "None"

    # Localização (bairro/cidade)
    try:
        location = imovel.find("h2", {"data-qa": "POSTING_CARD_LOCATION"}).text.strip()
    except Exception as e:
        location = "None"

    # Endereço (rua)
    try:
        street = imovel.find("div", {"class": "postingLocations-module__location-address-in-listing"}).text.strip()
    except Exception as e:
        street = "None"

    # Área, quartos, banheiros, vagas
    area = 0.0
    rooms = 0
    bathrooms = 0
    parking = 0
    try:
        features = imovel.find("h3", {"data-qa": "POSTING_CARD_FEATURES"})
        spans = features.find_all("span")
        list_values = []
        for span in spans:
            list_values.append(span.text.split()[0])
        area, rooms, bathrooms, parking = list_values[:4]

    except Exception as e:
        area = 0.0
        rooms = 0
        bathrooms = 0
        parking = 0

    # Preço
    try:
        price_txt = imovel.find("div", {"data-qa": "POSTING_CARD_PRICE"}).text
    except Exception as e:
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
        print(e.errors())
        return None

    return object_imovel.model_dump_json()


def get_important_data_brognoli(imovel: BeautifulSoup):
    # Título do imóvel
    try:
        title = imovel.find("a")["title"]
    except Exception as e:
        title = "None"

    # Link do imóvel
    try:
        link = imovel.find("a")['href']
    except Exception as e:
        link = "None"

    # Localização (bairro/cidade)
    try:
        location_full = imovel.find("span", {"class": "e"}).text.strip()
        if "," in location_full:
            street = location_full.split(",")[0].strip()
            location = location_full.split(",")[1].strip()
        else:
            street = location = location_full
    except Exception as e:
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
                except Exception as e:
                    parking = 0
    except Exception as e:
        area = 0.0
        rooms = 0
        bathrooms = 0
        parking = 0

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "v"}).text.strip()
    except Exception as e:
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
        return None

    return object_imovel.model_dump_json()
