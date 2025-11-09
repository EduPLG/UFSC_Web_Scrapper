from pydantic import ValidationError
from bs4 import BeautifulSoup
from models.imovel import ImovelCard
import json
from os.path import join
from os import makedirs
import re

PATH_OUTPUT = "output"


def save_elements_to_json(elements: list[dict], filename: str):
    """Salva uma lista de elementos em um arquivo JSON.

    Args:
        elements (list[dict]): Lista de elementos a serem salvos.
        filename (str): Nome do arquivo JSON onde os dados serão salvos.
    """
    if not filename.endswith(".json"):
        filename += ".json"

    elements_to_save = list(filter(lambda x: x is not None, elements))
    makedirs(PATH_OUTPUT, exist_ok=True)

    with open(join(PATH_OUTPUT, filename), "w", encoding="utf-8") as file:
        json.dump(elements_to_save, file, ensure_ascii=False, indent=4)


def get_elements_from_json(filename: str) -> list[ImovelCard]:
    """Lê uma lista de elementos de um arquivo JSON.

    Args:
        filename (str): Nome do arquivo JSON a ser lido.

    Returns:
        list[ImovelCard]: Lista de elementos lidos do arquivo JSON.
    """
    with open(join(PATH_OUTPUT, filename), "r", encoding="utf-8") as file:
        list_imovel_str = json.load(file)
    imoveis = []
    for imovel_json_str in list_imovel_str:
        if imovel_json_str:  # Garante que a string não é nula ou vazia
            imovel_dict = json.loads(imovel_json_str)
            imoveis.append(ImovelCard.model_validate(imovel_dict))
    return imoveis


def get_important_data_zapimoveis(imovel: BeautifulSoup):
    # Link do imóvel
    try:
        link = imovel.find("a")["href"]
    except Exception as e:
        link = None

    # Título do imóvel
    try:
        title = imovel.find("a")["title"]
    except Exception as e:
        title = None

    try:
        # Localização (bairro/cidade)
        location = imovel.find("h2", {"data-cy": "rp-cardProperty-location-txt"}).text or ""
        location = location.split("\n")[1] if "\n" in location else location
    except Exception as e:
        location = None

    # Endereço (rua)
    try:
        street = imovel.find("p", {"data-cy": "rp-cardProperty-street-txt"}).text.strip()
    except Exception as e:
        street = None

    # Área
    try:
        area_txt = imovel.find("li", {"data-cy": "rp-cardProperty-propertyArea-txt"}).text
        area = float(area_txt.split("\n")[-1].replace("m²", "").replace(",", ".").strip())
    except Exception as e:
        area = None

    # Banheiros
    try:
        bathrooms_txt = imovel.find("li", {"data-cy": "rp-cardProperty-bathroomQuantity-txt"}).text
        bathrooms = int(bathrooms_txt.split("\n")[-1])
    except Exception as e:
        bathrooms = None

    # Quartos
    try:
        rooms_txt = imovel.find("li", {"data-cy": "rp-cardProperty-bedroomQuantity-txt"}).text
        rooms = int(rooms_txt.split("\n")[-1])
    except Exception as e:
        rooms = None

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
        parking = None

    dados_imovel = {
        "title": title,
        "street": street,
        "url": link,
        "price_txt": price_txt,
        "local": location,
        "rooms": rooms,
        "area": area,
        "bathrooms": bathrooms,
        "parking": parking
    }

    # Filtre o dicionário, removendo chaves com valores "Nulos"
    dados_filtrados = {
        chave: valor for chave, valor in dados_imovel.items()
        if valor is not None
    }

    try:
        object_imovel = ImovelCard(**dados_filtrados)
    except ValidationError as e:
        return None

    return object_imovel.model_dump_json()


def get_important_data_imoveis_sc(imovel: BeautifulSoup):
    # Título do imóvel
    try:
        title = imovel.find("a").text.strip()
    except Exception as e:
        title = None

    # Link do imóvel
    try:
        link = imovel.find('a')["href"]
    except Exception as e:
        link = None

    # Localização (bairro/cidade)
    try:
        location = imovel.find("div", {"class": "imovel-extra"}).select_one("strong").get_text(strip=True)
    except Exception as e:
        location = None

    # Endereço (rua)  Esse site não fornece o endereço completo
    street = None

    # Área, quartos, banheiros, vagas
    area = None
    rooms = None
    bathrooms = None
    parking = None

    features = imovel.find("ul", {"class": "imovel-info"})

    # Primeiro, verifique se a <ul> foi encontrada
    if features:
        spans = features.select("li > span")
        if spans:
            for span in spans:
                text_ = span.get_text(strip=True)

                strong_tag = span.select_one("strong")

                if not strong_tag:
                    continue

                strong_text = strong_tag.get_text(strip=True)

                if 'm²' in text_:
                    try:
                        # CORREÇÃO: Substitui vírgula por ponto
                        area = float(strong_text.replace(",", "."))
                    except (ValueError, AttributeError):
                        pass

                elif 'quartos' in text_:
                    try:
                        rooms = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

                elif 'suíte' in text_:
                    try:
                        bathrooms = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

                elif 'vaga' in text_:
                    try:
                        parking = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "imovel-preco"}).text.strip()
    except Exception as e:
        price_txt = None

    dados_imovel = {
        "title": title,
        "street": street,
        "url": link,
        "price_txt": price_txt,
        "local": location,
        "rooms": rooms,
        "area": area,
        "bathrooms": bathrooms,
        "parking": parking
    }

    # Filtre o dicionário, removendo chaves com valores "Nulos"
    dados_filtrados = {
        chave: valor for chave, valor in dados_imovel.items()
        if valor is not None
    }

    try:
        object_imovel = ImovelCard(**dados_filtrados)
    except ValidationError as e:
        return None

    return object_imovel.model_dump_json()


def get_important_data_brognoli(imovel: BeautifulSoup):
    # Título do imóvel
    try:
        title = imovel.find("a")["title"]
    except Exception as e:
        title = None

    # Link do imóvel
    try:
        link = imovel.find("a")['href']
    except Exception as e:
        link = None

    # Localização (bairro/cidade)
    try:
        location_full = imovel.find("span", {"class": "e"}).text.strip()
        if "," in location_full:
            street = location_full.split(",")[0].strip()
            location = location_full.split(",")[1].strip()
        else:
            street = location = location_full
    except Exception as e:
        location = street = None

    # Área, quartos, banheiros, vagas
    area = None
    rooms = None
    bathrooms = None
    parking = None
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
        pass

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "v"}).text.strip()
    except Exception as e:
        price_txt = None

    dados_imovel = {
        "title": title,
        "street": street,
        "url": link,
        "price_txt": price_txt,
        "local": location,
        "rooms": rooms,
        "area": area,
        "bathrooms": bathrooms,
        "parking": parking
    }   

    # Filtre o dicionário, removendo chaves com valores "Nulos"
    dados_filtrados = {
        chave: valor for chave, valor in dados_imovel.items()
        if valor is not None
    }

    try:
        object_imovel = ImovelCard(**dados_filtrados)
    except ValidationError as e:
        return None

    return object_imovel.model_dump_json()

def get_important_data_adrianoimoveis(imovel: BeautifulSoup):
    BASE_URL = "https://www.adrianoimoveis.com.br"

    try:
        href = imovel.get("href") or ""
        url = href if href.startswith("http") else f"{BASE_URL}{href}"
    except Exception:
        url = "None"

    # Título
    try:
        title = (imovel.get("title") or "").strip()
        if not title:
            h = imovel.find(["h1", "h2", "h3", "h4"])
            title = (h.get_text(" ", strip=True) if h else imovel.get_text(" ", strip=True)).strip() or "None"
    except Exception:
        title = "None"

    # Texto bruto do card (pra usar nos outros elementos)
    try:
        card_text = imovel.get_text(" ", strip=True)
    except Exception:
        card_text = ""

    if len(card_text) < 10 and imovel.parent:
        try:
            card_text = f"{card_text} {imovel.parent.get_text(' ', strip=True)}".strip()
        except Exception:
            pass

    # Price / Área / Quartos / Banheiros / Vagas
    price_txt = None
    area = 0.0
    rooms = 0
    bathrooms = 0
    parking = 0
    location = ""
    street = ""

    try:
        m_price = re.search(r"R\$\s*[\d\.\,]+", card_text)
        price_txt = m_price.group(0) if m_price else None
    except Exception:
        price_txt = None

    try:
        m_area = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", card_text, flags=re.IGNORECASE)
        if m_area:
            val = m_area.group(1).replace(".", "").replace(",", ".")
            area = float(val)
    except Exception:
        area = 0.0

    try:
        m_rooms = re.search(r"(\d+)\s*(quartos?|dormit[óo]rios?)", card_text, flags=re.IGNORECASE)
        if m_rooms:
            rooms = int(m_rooms.group(1))
    except Exception:
        rooms = 0

    try:
        m_baths = re.search(r"(\d+)\s*banheiros?", card_text, flags=re.IGNORECASE)
        if m_baths:
            bathrooms = int(m_baths.group(1))
    except Exception:
        bathrooms = 0

    try:
        m_park = re.search(r"(\d+)\s*vagas?", card_text, flags=re.IGNORECASE)
        if m_park:
            parking = int(m_park.group(1))
    except Exception:
        parking = 0

    # Localização
    try:
        lines = [t.strip() for t in card_text.splitlines() if t.strip()]
        cand = [l for l in lines if "florian" in l.lower() or " - " in l]
        if cand:
            location = cand[-1]
    except Exception:
        location = ""

    try:
        obj = ImovelCard(
            title=title or "None",
            street=street or "",
            url=url,
            price_txt=price_txt,
            location=location or "",
            rooms=rooms,
            area=area,
            bathrooms=bathrooms,
            parking=parking
        )

    except ValidationError:
        return None

    return obj.model_dump_json()


