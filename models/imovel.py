from pydantic import BaseModel, HttpUrl, Field, model_validator
import re


class ImovelCard(BaseModel):
    url: HttpUrl
    title: str = Field(..., description="Título do anúncio")
    local: str = Field(None, description="Localização do imóvel (bairro/cidade)")
    street: str = Field(None, description="Endereço do imóvel (rua)")
    price_txt: str = Field(..., description="Valor do imóvel formatado (ex: 'R$ 850.000,00')")
    price_num: float = Field(None, description="Valor numérico do imóvel em reais")
    area: float = Field(None, description="Área do imóvel em metros quadrados")
    rooms: int = Field(None, description="Número de quartos")
    parking: int = Field(None, description="Número de vagas na garagem")
    bathrooms: int = Field(None, description="Número de banheiros")

    @model_validator(mode="after")
    def _fill_valor_num(self):
        bruto = (
            # self.price_txt.replace("R$", "").replace(" ", "").replace(",", ".")
            re.sub(r"[^0-9,\.]", "", self.price_txt).replace(".", "").replace(",", ".")
        )
        try:
            self.price_num = float(bruto)
        except ValueError as e:
            raise ValueError("Não foi possível converter para numero") from e
        return self
