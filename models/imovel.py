from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, model_validator

class ImovelCard(BaseModel):
    url: HttpUrl
    titulo: str = Field(..., description="Título do anúncio")
    valor_texto: str = Field(..., description="Valor do imóvel formatado (ex: 'R$ 850.000,00')")
    valor_num: Optional[float] = Field(None, description="Valor numérico do imóvel em reais")
    area: Optional[float] = Field(None, description="Área do imóvel em metros quadrados")
    quartos: Optional[int] = Field(None, description="Número de quartos")
    vagas: Optional[int] = Field(None, description="Número de vagas na garagem")
    banheiros: Optional[int] = Field(None, description="Número de banheiros")

    @model_validator(mode="after")
    def _fill_valor_num(self):

        bruto = (
            self.valor_texto
              .replace("R$", "")
              .replace(" ", "")
              .replace(".", "")
              .replace(",", ".")
        )
        try:
            self.valor_num = float(bruto)
        except ValueError as e:
            raise ValueError(f"Não foi possível converter para numero") from e
        return self
