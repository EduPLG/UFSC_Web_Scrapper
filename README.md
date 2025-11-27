# Web Scrapper de Imóveis - UFSC

Este projeto é um trabalho da disciplina INE5454 - Tópicos Especiais em Gerência de Dados da UFSC. O objetivo é realizar web scraping em sites de imobiliárias, coletar dados de imóveis e realizar análises comparativas de preços e áreas (m²) entre diferentes cidades e bairros.

## Sites de Imobiliárias

Os seguintes sites são utilizados para a coleta de dados:

-   [Adriano Imóveis](https://www.adrianoimoveis.com.br)
-   [Brognoli](https://www.brognoli.com.br)
-   [Imóveis SC](https://www.imoveis-sc.com.br)

## Funcionalidades

-   **Web Scraping:** Coleta automatizada de dados de imóveis dos sites especificados.
-   **Análise de Dados:**
    -   Comparação de preços por metro quadrado (m²) entre cidades e bairros.
    -   Geração de estatísticas descritivas (média, mediana, contagem) para cada localidade.
-   **Exportação de Dados:** Salva os dados coletados e analisados em formatos JSON e CSV.
-   **Visualizações:** Criação de gráficos para facilitar a visualização das análises.

## Como Usar
1.  **Opcional: Configuração do Ambiente (Se quiser utilizar metabase para a análize)**
    -   Certifique-se de ter o [Docker](https://www.docker.com/products/docker-desktop/) e o Docker Compose instalados.
    -   Na primeira vez ou sempre que alterar as dependências (`requirements.txt`), construa as imagens com o comando:

    ```bash
    docker-compose up --build
    ```

2.  **Opcinal: Execução Interativa do Scrapper:**
    -   Para iniciar a aplicação e interagir com o menu principal, execute o seguinte comando. Ele irá iniciar todos os serviços necessários (`mongo`, `metabase`) e conectar seu terminal ao script principal:
    ```bash
    docker-compose run --rm scraper
    ```
3.  **Menu Interativo:**
    -   O script oferece um menu interativo para selecionar as opções de scraping e análise.
    -   As opções incluem:
        -   Executar o scraping para todas as opções disponíveis.
        -   Selecionar uma cidade específica.
        -   Definir o tipo de transação (aluguel ou compra).
        -   Executar o scraping para a cidade selecionada.
        -   Salvar os dados em arquivos JSON e CSV.
        -   Executar a análise completa dos dados.
4.  **Análise dos Dados:**
    -   Após a execução do scraping e análise, os resultados estarão disponíveis em arquivos CSV e JSON na pasta `output`.
    -   Gráficos e relatórios resumidos também serão gerados na pasta `output`.
