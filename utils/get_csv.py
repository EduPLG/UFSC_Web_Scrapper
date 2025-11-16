import os
import pandas as pd
from utils.get_data_func import get_elements_from_json, FOLDER_JSON


# From output, get de first file
def generate_df(tipo: str = None) -> pd.DataFrame:
    """
    Lê todos os arquivos JSON e retorna um DataFrame consolidado.
    Pode filtrar por tipo de transação ('aluguel' ou 'venda') com base no nome do arquivo.
    """
    ALL_DF = []
    file_names = [f for f in os.listdir(FOLDER_JSON) if f.endswith(".json")]

    if tipo in ["aluguel", "venda"]:
        file_names = [f for f in file_names if tipo in f.lower()]
        print(f"🔍 Filtrando arquivos do tipo '{tipo}' ({len(file_names)} encontrados)")
    else:
        print(f"🔍 Nenhum filtro de tipo aplicado ({len(file_names)} arquivos)")

    for file in file_names:
        try:
            lista_de_imoveis = get_elements_from_json(file)
            if not lista_de_imoveis:
                continue
            data_for_dataframe = [imovel.model_dump() for imovel in lista_de_imoveis]
            ALL_DF.append(pd.DataFrame(data_for_dataframe))
        except Exception as e:
            print(f"Erro ao carregar {file}: {e}")

    if not ALL_DF:
        print("⚠️ Nenhum DataFrame válido encontrado!")
        return pd.DataFrame()

    final_df = pd.concat(ALL_DF, ignore_index=True)
    print(f"✅ {len(final_df)} registros combinados.")
    return final_df




if __name__ == "__main__":
    df = generate_df()
    df.to_csv("output/data_base.csv", na_rep='NULL', index=False)
