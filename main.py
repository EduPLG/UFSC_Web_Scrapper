from utils.get_csv import generate_df
from models.site import Site


class Estilos:
    """Classe para armazenar códigos de escape ANSI para estilização de texto no terminal."""
    # Estilos
    RESET = '\033[0m'
    BOLD = '\033[1m'
    # Cores (texto)
    YELLOW = '\033[93m'


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
    print(
        f"\n           ================== MENU PRINCIPAL ======================\n"
        "1. Executar Scrapping de todas as opções disponíveis\n"
        f"2. Selecionar Cidade: (atual: {Estilos.BOLD}{Estilos.YELLOW}{CIDADES.get(city)}{Estilos.RESET})\n"
        f"3. Tipo de transação (Alugar/Comprar): (atual: {Estilos.BOLD}{Estilos.YELLOW}{'Alugar' if aluguel else 'Comprar'}{Estilos.RESET})\n"
        f"4. Executar Scrapping de {Estilos.BOLD}{Estilos.YELLOW}{CIDADES.get(city)}{Estilos.RESET} para {Estilos.BOLD}{Estilos.YELLOW}{'Alugar' if aluguel else 'Comprar'}{Estilos.RESET}\n"
        "5. Salvar dados em CSV\n"
        "6. Sair\n"
        f"           ========================================================\n"
    )
    while True:
        choice = input("Selecione uma opção: _ ")
        if choice.isnumeric() and 1 <= int(choice) <= 6:
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
                df.to_csv("output/data_base.csv", na_rep='NULL', index=False)
                print("Arquivo CSV salvo com sucesso!")
            case 6:
                print("Saindo...")
                break
