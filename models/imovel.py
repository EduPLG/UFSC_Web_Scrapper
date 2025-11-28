from pydantic import BaseModel, HttpUrl, Field, model_validator
import re


class ImovelCard(BaseModel):
    url: HttpUrl
    titulo: str | None = Field(None, description="Título do anúncio")
    local_txt: str | None = Field(..., description="Localização do imóvel (bairro/cidade)")
    cidade: str | None = Field(None, description="Cidade do imóvel (ex: Florianópolis)")
    bairro: str | None = Field(None, description="Bairro do imóvel (ex: Capoeiras)")
    rua: str | None = Field(None, description="Endereço do imóvel (rua)")
    price_txt: str = Field(..., description="Valor do imóvel formatado (ex:'R$ 850.000,00')")
    price_num: float | None = Field(None, description="Valor numérico do imóvel em reais")
    area: float | None = Field(None, description="Área do imóvel em metros quadrados")
    quartos: int | None = Field(None, description="Número de quartos")
    garagem: int | None = Field(None, description="Número de vagas na garagem")
    banheiros: int | None = Field(None, description="Número de banheiros")
    tipo: str | None = Field(None, description="Aluguel ou Venda")

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
                self.cidade = parts[0].title()
                self.bairro = parts[1].title()
                return

        # Tenta o padrão "Bairro - Cidade"
        if '-' in local:
            parts = [p.strip() for p in local.split('-')]
            if len(parts) >= 2:
                # O padrão mais comum é Bairro - Cidade
                self.bairro = parts[0].title()
                self.cidade = parts[1].title()
                return

        # Se nenhum padrão acima funcionar, assume que o texto é a cidade
        self.cidade = local.title()
        if self.bairro is None and self.rua is not None and '-' in self.rua:
            rua_parts = [p.strip() for p in self.rua.split('-')]
            if len(rua_parts) >= 2:
                self.rua = rua_parts[0].title()
                self.bairro = rua_parts[1].title()

    @model_validator(mode="after")
    def _fill_computed_fields(self) -> "ImovelCard":
        self._fill_valor_num()
        self._fill_locals()
        return self
