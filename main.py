from utils.analise import run_complete_analysis
from utils.get_csv import generate_df
from utils.get_data_func import PATH_OUTPUT, FOLDER_JSON
from os.path import join
import os
from models.site import Site


class Estilos:
    """Classe para armazenar códigos de escape ANSI para estilização de texto no terminal."""
    # Estilos
    RESET = '\033[0m'
    BOLD = '\033[1m'
    # Cores (texto)
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'


CIDADES = {
    "florianopolis": "Florianópolis",
    "sao-jose": "São José",
    "palhoca": "Palhoça",
    "biguacu": "Biguacu"
}


def generate_obj(name: str) -> Site:
    return Site.factory(name)


def troca_cidade(atual: str) -> str:
    print(f"\nCidade atual: {CIDADES.get(atual)}")
    print("Cidades disponíveis:")
    # Imprime a lista de cidades dinamicamente
    for i, cidade_nome in enumerate(CIDADES.values(), 1):
        print(f"{i}. {cidade_nome}")

    while True:
        choice = input("Selecione uma opção: _ ")
        if choice.isnumeric() and 1 <= int(choice) <= len(CIDADES):
            # Converte a escolha para o índice da lista de chaves
            return list(CIDADES.keys())[int(choice) - 1]
        else:
            print("Opção inválida. Tente novamente.")


def menu(city: str, aluguel: bool) -> int:
    arq_json = True if (os.path.exists(FOLDER_JSON) and list(filter(lambda x: x.endswith(".json"), os.listdir(FOLDER_JSON)))) else False
    data_base = True if (os.path.exists(PATH_OUTPUT) and list(filter(lambda x: x.startswith("data_base."), os.listdir(PATH_OUTPUT)))) else False

    print(
        "\n           ================== MENU PRINCIPAL ======================\n"
        f"1. {Estilos.BLUE}Executar Scrapping de todas as opções disponíveis{Estilos.RESET}\n"
        f"2. Selecionar Cidade: (atual: {Estilos.YELLOW}{CIDADES.get(city)}{Estilos.RESET})\n"
        f"3. Tipo de transação (Alugar/Comprar): (atual: {Estilos.YELLOW}{'Alugar' if aluguel else 'Comprar'}{Estilos.RESET})\n"
        f"4. Executar Scrapping de {Estilos.YELLOW}{CIDADES.get(city)}{Estilos.RESET} para {Estilos.YELLOW}{'Alugar' if aluguel else 'Comprar'}{Estilos.RESET}\n"
        f"5. Salvar dados em um {Estilos.BOLD}json{Estilos.RESET} e {Estilos.BOLD}csv{Estilos.RESET} {"" if arq_json else "⚠️ Falta arquivos do Scrapping"}\n"
        f"6. {Estilos.GREEN}Executar análise completa dos dados{Estilos.RESET} {"" if data_base else "⚠️ Falta dados do csv"}\n"
        "7. Sair\n"
        "           ========================================================\n"
    )
    while True:
        choice = input("Selecione uma opção: _ ")
        if choice.isnumeric() and 1 <= int(choice) <= 7 and not (choice == "5" and not arq_json) and not (choice == "6" and not data_base):
            return int(choice)
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    cidade_atual = "florianopolis"
    aluguel_atual = True
    todas_cidades = ["florianopolis", "sao-jose", "palhoca", "biguacu"]
    sites = [generate_obj("Brognoli"),
             generate_obj("Imoveis_SC"),
             generate_obj("AdrianoImoveis")]

    while True:
        escolha = menu(city=cidade_atual, aluguel=aluguel_atual)

        match escolha:
            case 1:
                print("Executando Scrapping para todas as opções...")
                for aluguel in [True, False]:
                    for cidade in todas_cidades:
                        for obj_site in sites:
                            obj_site.start_web_scrapping(city=cidade, aluguel=aluguel)
                print("Scrapping concluído!")
            case 2:
                cidade_atual = troca_cidade(cidade_atual)
            case 3:
                aluguel_atual = not aluguel_atual
                print(f"Tipo de transação alterado para: {'Alugar' if aluguel_atual else 'Comprar'}")
            case 4:
                print(f"Executando Scrapping para {CIDADES.get(cidade_atual)} ({'Alugar' if aluguel_atual else 'Comprar'})...")
                for obj_site in sites:
                    obj_site.start_web_scrapping(city=cidade_atual, aluguel=aluguel_atual)
                print("Scrapping concluído!")
            case 5:
                print("Gerando arquivo CSV...")
                df = generate_df()
                df.to_csv(
                    join(PATH_OUTPUT, "data_base.csv"),
                    na_rep='NULL',
                    index=False
                )
                print("Arquivo CSV salvo com sucesso!")
                print("Gerando arquivo JSON...")
                df.to_json(
                    join(PATH_OUTPUT, "data_base.json"), orient="records",
                    force_ascii=False,
                    indent=4
                )
                print("Arquivo JSON salvo com sucesso!")
            case 6:
                if not filter(lambda x: x.startswith("data_base."), os.listdir(PATH_OUTPUT)):
                    print("Nenhum arquivo de dados encontrado. Por favor, execute o scrapping e salve os dados primeiro.")
                    continue
                print("Selecione o tipo de análise:")
                print("1. Apenas ALUGUEL")
                print("2. Apenas VENDA")
                print("3. Todos os tipos (misturado)")

                tipo_choice = input("Escolha uma opção: _ ")
                if tipo_choice == "1":
                    tipo = "aluguel"
                elif tipo_choice == "2":
                    tipo = "venda"
                else:
                    tipo = None

                run_complete_analysis(verbose=True, tipo=tipo)

            case 7:
                print("Saindo...")
                break
