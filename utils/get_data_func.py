from pydantic import ValidationError
from bs4 import BeautifulSoup
from models.imovel import ImovelCard
import json
from os.path import join
from os import makedirs

PATH_OUTPUT = "output"
FOLDER_JSON = join(PATH_OUTPUT, "json_files")


def save_elements_to_json(elements: list[ImovelCard], filename: str):
    """Salva uma lista de elementos em um arquivo JSON.

    Args:
        elements (list[dict]): Lista de elementos a serem salvos.
        filename (str): Nome do arquivo JSON onde os dados serão salvos.
    """
    if not filename.endswith(".json"):
        filename += ".json"

    elements_to_save = list(filter(lambda x: x is not None, elements))
    elements_to_save = [el.model_dump(mode="json") for el in elements_to_save]

    makedirs(FOLDER_JSON, exist_ok=True)

    with open(join(FOLDER_JSON, filename), "w", encoding="utf-8") as file:
        json.dump(elements_to_save, file, ensure_ascii=False, indent=4)


def get_elements_from_json(filename: str) -> list[ImovelCard]:
    """Lê uma lista de elementos de um arquivo JSON.

    Args:
        filename (str): Nome do arquivo JSON a ser lido.

    Returns:
        list[ImovelCard]: Lista de elementos lidos do arquivo JSON.
    """
    with open(join(FOLDER_JSON, filename), "r", encoding="utf-8") as file:
        list_imovel = json.load(file)
    imoveis = []
    for imovel_json in list_imovel:
        if imovel_json:  # Garante que a string não é nula ou vazia
            imoveis.append(ImovelCard.model_validate(imovel_json))
    return imoveis


def get_important_data_imoveis_sc(imovel: BeautifulSoup, aluguel: bool)-> ImovelCard | None:
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
    rua = None

    # Área, quartos, banheiros, vagas
    area = None
    quartos = None
    banheiros = None
    garagem = None

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
                        quartos = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

                elif 'suíte' in text_:
                    try:
                        banheiros = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

                elif 'vaga' in text_:
                    try:
                        garagem = int(strong_text)
                    except (ValueError, AttributeError):
                        pass

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "imovel-preco"}).text.strip()
    except Exception as e:
        price_txt = None

    dados_imovel = {
        "titulo": title,
        "rua": rua,
        "url": link,
        "price_txt": price_txt,
        "local_txt": location,
        "quartos": quartos,
        "area": area,
        "banheiros": banheiros,
        "garagem": garagem,
        "tipo": "aluguel" if aluguel else "venda"
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

    return object_imovel


def get_important_data_brognoli(imovel: BeautifulSoup, aluguel: bool) -> ImovelCard | None:
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
            rua = location_full.split(",")[0].strip()
            location = location_full.split(",")[1].strip()
        else:
            rua = location = location_full
    except Exception as e:
        location = rua = None

    # Área, quartos, banheiros, vagas
    area = None
    quartos = None
    banheiros = None
    garagem = None
    try:
        features = imovel.find_all("li")
        for feature in features:
            text = feature.text.strip().lower()
            if 'm²' in text:
                area = float(text.replace('m²', '').strip())
            elif 'quartos' in text or 'dormitório' in text:
                quartos = int(text.split()[0])
            elif 'banheiro' in text:
                banheiros = int(text.split()[0])
            else:
                try:
                    garagem = int(text.strip())
                except Exception as e:
                    garagem = 0
    except Exception as e:
        pass

    # Preço
    try:
        price_txt = imovel.find("span", {"class": "v"}).text.strip()
    except Exception as e:
        price_txt = None

    dados_imovel = {
        "titulo": title,
        "rua": rua,
        "url": link,
        "price_txt": price_txt,
        "local_txt": location,
        "quartos": quartos,
        "area": area,
        "banheiros": banheiros,
        "garagem": garagem,
        "tipo": "aluguel" if aluguel else "venda"
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

    return object_imovel


def get_important_data_adrianoimoveis(imovel: BeautifulSoup, aluguel: bool) -> ImovelCard | None:
    BASE_URL = "https://www.adrianoimoveis.com.br"

    pricestxt = imovel.find_all("p", class_="card-with-buttons__value")
    
    if len(pricestxt) != 1:
        # Impedir que pegue imoveis com mais de um preço
        return None

    try:
        href = imovel.get("href") or ""
        url = href if href.startswith("http") else f"{BASE_URL}{href}"
    except Exception:
        url = None

    # Título
    try:
        title = imovel.find("p", {"class": "card-with-buttons__title"}).text.strip()
    except Exception:
        title = None

    # Texto bruto do card (pra usar nos outros elementos)
    try:
        location = imovel.find("h2", {"class": "card-with-buttons__heading"}).text.strip()
    except Exception:
        location = None

    try:
        price_txt = imovel.find("p", {"class": "card-with-buttons__value"}).text.strip()
    except Exception:
        price_txt = None

    # Price / Área / Quartos / Banheiros / Vagas
    area = None
    quartos = None
    banheiros = None
    garagem = None
    rua = None
    atributos = None
    try:
        # Encontra a tag 'ul' que NÃO possui o atributo 'class'
        atributos = imovel.find("ul", class_=False)
    except Exception:
        pass
    if atributos is not None:
        lista_atr = atributos.find_all("li")
        for atrib in lista_atr:
            text = atrib.text.strip().lower()
            if 'm²' in text:
                try:
                    area = float(text.replace('m²', '').strip())
                except Exception:
                    pass
            elif 'quarto' in text:
                try:
                    quartos = int(text.split()[0])
                except Exception:
                    pass
            elif 'banheiro' in text:
                try:
                    banheiros = int(text.split()[0])
                except Exception:
                    pass
            elif 'vaga' in text:
                try:
                    garagem = int(text.split()[0])
                except Exception:
                    pass
            elif 'suíte' in text:
                if banheiros is None:
                    banheiros = 0
                banheiros += 1

    try:
        object_imovel = ImovelCard(
            url=url,
            titulo=title,
            local_txt=location,
            rua=rua,
            price_txt=price_txt,
            area=area,
            quartos=quartos,
            garagem=garagem,
            banheiros=banheiros,
            tipo="aluguel" if aluguel else "venda"
        )
    except ValidationError:
        return None

    return object_imovel
