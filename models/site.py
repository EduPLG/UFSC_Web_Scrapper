from typing import Any
from collections.abc import Callable
from pydantic import BaseModel, HttpUrl, Field
from bs4 import BeautifulSoup
import re
from playwright.sync_api import Page

from utils.scrap_func import save_site_content
from utils.next_pag_func import (
    next_page_zapimoveis,
    next_page_brognoli,
    next_page_imoveis_sc
)
from utils.get_data_func import (
    get_important_data_zapimoveis,
    get_important_data_brognoli,
    get_important_data_imoveis_sc
)


class Site(BaseModel):
    """
    Modelo base para representar um site a ser raspado.
    Use instâncias deste modelo ou de suas subclasses para iniciar o scraping.
    """
    name: str = Field(None, description="Nome do site")
    url: HttpUrl = Field(None, description="URL base do site para scraping")
    filter: tuple[str, dict[str, Any]] = Field(None, description="Filtro para encontrar os elementos dos imóveis")
    func_get_data: Callable[[BeautifulSoup], str | None] = Field(None, description="Função para extrair os dados importantes de um imóvel")
    func_next_page: Callable[[Page], bool] = Field(None, description="Função para navegar para a próxima página")
    json_name: str = Field(None, description="Nome do arquivo JSON para salvar os dados extraídos")

    model_config = {"arbitrary_types_allowed": True}

    def prepare_filter_url(self,
                           city: str,
                           aluguel: bool) -> str:
        """
        TO_BE_IMPLEMENTED_IN_SUBCLASSES

        Prepara a URL com filtros adicionais para o estado, cidade e tipo de transação.
        """
        return ""

    def start_web_scrapping(self,
                            city: str = "florianopolis",
                            aluguel: bool = True) -> None:
        """
        Inicia o processo de scraping usando os utilitários existentes.
        Apenas cidades de Santa Catarina são suportadas atualmente.
        Args:
            city (str): Nome da cidade para filtrar os imóveis.
            aluguel (bool): True para filtrar por aluguel, False para venda.
        """
        url_plus_filters = self.prepare_filter_url(city, aluguel)
        save_site_content(
            url_plus_filters,
            self.filter,
            self.func_get_data,
            self.func_next_page,
            self.json_name + "_" + city + ("_aluguel" if aluguel else "_venda")
        )

    @classmethod
    def factory(cls, name: str) -> "Site":
        """
        Cria uma instância da subclasse a partir de um nome.
        O nome é normalizado para encontrar a classe correspondente no registro.
        """
        def normalized_name(name: str) -> str:
            return re.sub(r"[-_\s]", "", name.lower().strip())
        normal_name = normalized_name(name)

        for subclass in cls.__subclasses__():
            # Extrai o nome da classe (ex: 'Site_ZapImoveis' -> 'ZapImoveis')
            subclass_simple_name = normalized_name(subclass.__name__.replace("Site_", ""))

            # Compara o nome normalizado com o nome da subclasse
            if subclass_simple_name == normal_name:
                return subclass()

        available_sites = [normalized_name(s.__name__.replace("Site_", "")) for s in cls.__subclasses__()]
        raise ValueError(f"Chave de site desconhecida: {name!r}. Opções disponíveis: {', '.join(available_sites)}")


class Site_ZapImoveis(Site):
    name: str = "zapimoveis"
    url: HttpUrl = "https://www.zapimoveis.com.br"
    filter: tuple[str, dict[str, Any]] = ("li", {"data-cy": "rp-property-cd"})
    func_get_data: Callable[[BeautifulSoup], str | None] = get_important_data_zapimoveis
    func_next_page: Callable[[Page], bool] = next_page_zapimoveis
    json_name: str = "zapimoveis"

    def prepare_filter_url(self,
                           city: str,
                           aluguel: bool) -> str:
        tipo = "aluguel" if aluguel else "venda"
        base = str(self.url).rstrip("/")  # converte HttpUrl para str
        return f"{base}/{tipo}/imoveis/sc+{city}"


class Site_Imoveis_SC(Site):
    name: str = "imoveis_sc"
    url: HttpUrl = "https://www.imoveis-sc.com.br"
    filter: tuple[str, dict[str, Any]] = ("div", {"class": "imovel-data"})
    func_get_data: Callable[[BeautifulSoup], str | None] = get_important_data_imoveis_sc
    func_next_page: Callable[[Page], bool] = next_page_imoveis_sc
    json_name: str = "imoveis_sc"

    def prepare_filter_url(self,
                           city: str,
                           aluguel: bool) -> str:
        tipo = "alugar" if aluguel else "comprar"
        base = str(self.url).rstrip("/")
        return f"{base}/{city}/{tipo}"


class Site_Brognoli(Site):
    name: str = "brognoli"
    url: HttpUrl = "https://www.brognoli.com.br"
    filter: tuple[str, dict[str, Any]] = ("article", {"class": "imovel"})
    func_get_data: Callable[[BeautifulSoup], str | None] = get_important_data_brognoli
    func_next_page: Callable[[Page], bool] = next_page_brognoli
    json_name: str = "brognoli"

    def prepare_filter_url(self,
                           city: str,
                           aluguel: bool) -> str:
        tipo = "alugar" if aluguel else "comprar"
        base = str(self.url).rstrip("/")
        return f"{base}/{tipo}/cidade/{city}/1"
