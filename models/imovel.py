from pydantic import BaseModel, HttpUrl, Field, model_validator
import re


class ImovelCard(BaseModel):
    url: HttpUrl
    title: str | None = Field(None, description="Título do anúncio")
    local_txt: str | None = Field(..., description="Localização do imóvel (bairro/cidade)")
    city: str | None = Field(None, description="Cidade do imóvel (ex: Florianópolis)")
    neighborhood: str | None = Field(None, description="Bairro do imóvel (ex: Capoeiras)")
    street: str | None = Field(None, description="Endereço do imóvel (rua)")
    price_txt: str = Field(..., description="Valor do imóvel formatado (ex:'R$ 850.000,00')")
    price_num: float | None = Field(None, description="Valor numérico do imóvel em reais")
    area: float | None = Field(None, description="Área do imóvel em metros quadrados")
    rooms: int | None = Field(None, description="Número de quartos")
    parking: int | None = Field(None, description="Número de vagas na garagem")
    bathrooms: int | None = Field(None, description="Número de banheiros")

    def _fill_valor_num(self) -> None:
        bruto = (
            re.sub(r"[^0-9,]", "", self.price_txt).replace(",", ".")
        )
        try:
            self.price_num = float(bruto)
        except ValueError as e:
            raise ValueError("Não foi possível converter para numero") from e

    def _fill_locals(self) -> None:
        local = self.local_txt.strip()

        # Remove o estado (SC) e informações extras, como nome do prédio
        local = re.sub(r'\s*-\s*SC.*$', '', local, flags=re.IGNORECASE)
        local = re.sub(r'/SC.*$', '', local, flags=re.IGNORECASE)

        # Tenta o padrão "Cidade, Bairro"
        if ',' in local:
            parts = [p.strip() for p in local.split(',')]
            if len(parts) >= 2:
                self.city = parts[0].title()
                self.neighborhood = parts[1].title()
                return

        # Tenta o padrão "Bairro - Cidade"
        if '-' in local:
            parts = [p.strip() for p in local.split('-')]
            if len(parts) >= 2:
                # O padrão mais comum é Bairro - Cidade
                self.neighborhood = parts[0].title()
                self.city = parts[1].title()
                return

        # Se nenhum padrão acima funcionar, assume que o texto é a cidade
        self.city = local.title()

    @model_validator(mode="after")
    def _fill_computed_fields(self) -> "ImovelCard":
        self._fill_valor_num()
        self._fill_locals()
        return self
