from utils.get_csv import generate_df
from utils.funcoesAnalise import DataAnalyzer
from pathlib import Path


def run_complete_analysis(verbose: bool = True, tipo: str = None) -> dict:
    print("=" * 80)
    print(f"ANÁLISE DE DADOS DE IMÓVEIS ({tipo.upper() if tipo else 'GERAL'})")
    print("=" * 80)
    print()
    
    print("1. Carregando dados dos arquivos JSON...")
    df = generate_df(tipo=tipo)
    
    if df.empty:
      print("ERRO: Nenhum dado encontrado! Verifique se já rodou o scraping e se o tipo está correto.")
      return
    
    print(f"✓ {len(df)} registros carregados")
    print()
    
    analyzer = DataAnalyzer(df)
    
    print("2. Limpando dados (removendo registros sem price_num ou area)...")
    df_clean = analyzer.limpaDados()
    print()
    
    print("3. Calculando preço por m² para cada imóvel...")
    df_with_price_per_m2 = analyzer.CalculaPrecoM2()
    print()
    
    print("4. Agrupando dados por cidade...")
    grouped_city = analyzer.group_by_location(by='city')
    print(f"✓ {len(grouped_city)} cidades analisadas")
    print("\nTop 5 cidades (por preço médio/m²):")
    print(grouped_city[['city', 'price_per_m2_mean', 'price_per_m2_median', 'price_per_m2_count']].head())
    print()
    
    print("5. Agrupando dados por bairro...")
    grouped_neighborhood = analyzer.group_by_location(by='neighborhood')
    print(f"✓ {len(grouped_neighborhood)} bairros analisados")
    print("\nTop 5 bairros (por preço médio/m²):")
    print(grouped_neighborhood[['neighborhood', 'price_per_m2_mean', 'price_per_m2_median', 'price_per_m2_count']].head())
    print()
    
    print("6. Agrupando dados por cidade e bairro...")
    grouped_both = analyzer.group_by_location(by='both')
    print(f"✓ {len(grouped_both)} combinações cidade/bairro analisadas")
    print()
    
    output_path = Path('output')
    output_path.mkdir(exist_ok=True)
    
    print("7. Salvando dados agrupados...")
    grouped_city.to_csv(output_path / 'agrupado_cidade.csv', index=False)
    print(f"✓ Dados por cidade salvos em: {output_path / 'agrupado_cidade.csv'}")
    
    grouped_neighborhood.to_csv(output_path / 'agrupado_bairro.csv', index=False)
    print(f"✓ Dados por bairro salvos em: {output_path / 'agrupado_bairro.csv'}")
    
    grouped_both.to_csv(output_path / 'agrupado_cidade_bairro.csv', index=False)
    print(f"✓ Dados por cidade/bairro salvos em: {output_path / 'agrupado_cidade_bairro.csv'}")
    print()
    
    print("8. Salvando DataFrame limpo...")
    df_with_price_per_m2.to_csv(output_path / 'data_base_clean.csv', index=False, na_rep='NULL')
    df_with_price_per_m2.to_json(
        output_path / 'data_base_clean.json',
        orient='records',
        force_ascii=False,
        indent=4
    )
    print(f"✓ DataFrame limpo salvo em: {output_path / 'data_base_clean.csv'}")
    print(f"✓ DataFrame limpo salvo em: {output_path / 'data_base_clean.json'}")
    print()
    
    print("9. Gerando visualizações...")
    saved_files = analyzer.criaTotalsVisualizacoes(output_path='output/graficos')
    print(f"✓ {len(saved_files)} gráficos criados")
    for file in saved_files:
        print(f"  - {file}")
    print()
    
    print("10. Gerando relatório resumido...")
    report_path = analyzer.GerarRelatorio(output_path='output')
    print(f"✓ Relatório salvo em: {report_path}")
    print()
    
    print("=" * 80)
    print("ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  📊 Gráficos: output/graficos/")
    print("  📄 Dados agrupados: output/agrupado_*.csv")
    print("  🧹 Dados limpos: output/data_base_clean.csv")
    print("  📝 Relatório: output/relatorio_analise.txt")
    print()


    return {
            "success": True,
            "files": saved_files,
            "stats": {
                  "total_graphs": len(saved_files),
                  "clean_records": len(df_clean)
            }
      }