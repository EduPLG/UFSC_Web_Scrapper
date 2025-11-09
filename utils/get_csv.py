import os
import pandas as pd
import numpy as np
from utils.get_data_func import get_elements_from_json, PATH_OUTPUT


# From output, get de first file
def generate_df() -> pd.DataFrame:
    ALL_DF = []
    file_names = list(filter(lambda x: x.endswith(".json"), os.listdir(PATH_OUTPUT)))
    for file in file_names:
        try:
            lista_de_imoveis = get_elements_from_json(file)
        except Exception as e:
            print(f"Erro ao carregar imóveis do arquivo {file}: {e}")

        if lista_de_imoveis:
            # 1. Converter a lista de objetos ImovelCard em uma lista de dicionários
            # O método .model_dump() do Pydantic é ideal para isso.
            data_for_dataframe = [imovel.model_dump() for imovel in lista_de_imoveis]

            # 2. Criar o DataFrame do Pandas a partir da lista de dicionários
            ALL_DF.append(pd.DataFrame(data_for_dataframe))

    if not ALL_DF:
        print("Data Frame vazio!")
        return pd.DataFrame()

    final_df = pd.concat(ALL_DF, ignore_index=True)
    return final_df


if __name__ == "__main__":
    df = generate_df()
    df.to_csv("output/data_base.csv", na_rep='NULL', index=False)
