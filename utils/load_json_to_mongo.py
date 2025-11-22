import os
from pymongo import MongoClient
from models.imovel import ImovelCard

# Config do Mongo (pega default do docker compose se não tivermos no env)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://imoveis:imoveis@mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "imoveis_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "imoveis")

_mongo_client = MongoClient(MONGO_URI)

def save_elements_to_mongo(elements: list[ImovelCard], json_name: str) -> None:
    """Salva uma lista de ImovelCard no MongoDB."""
    docs = [el.model_dump(mode="json") for el in elements if el is not None]
    if not docs:
        return

    collection_name = _get_collection_name(json_name)
    print(collection_name)
    _mongo_collection = _mongo_client[MONGO_DB_NAME][collection_name]
    _mongo_collection.insert_many(docs)

def _get_imovel_type(json_name: str):
    base = json_name[:-5] if json_name.endswith(".json") else json_name

    try:
        _, _, tipo = base.rsplit("_", 2)
        return tipo
    except ValueError:
        return None


def _get_collection_name(json_name) -> str:
    tipo = _get_imovel_type(json_name)
    if not tipo:
        return "imoveis_desconhecido"

    tipo_lower = tipo.lower()
    if tipo_lower in ("aluguel"):
        return "imoveis_aluguel"
    if tipo_lower in ("venda"):
        return "imoveis_venda"

    return f"imoveis_{tipo_lower}"