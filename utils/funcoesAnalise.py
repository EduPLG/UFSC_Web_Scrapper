import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Literal

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class DataAnalyzer:
    
    def __init__(self, dados: pd.DataFrame):
        self.dados = dados.copy()
        self.dadosLimpos = None
        
    def limpaDados(self) -> pd.DataFrame:
        print("Limpando dados...")
        quantidadeInicial = len(self.dados)
        # remove valores zerados, nulos ou negativos (pouco provavel ter)
        self.dadosLimpos = self.dados.dropna(subset=['price_num', 'area'])
        self.dadosLimpos = self.dadosLimpos[
            (self.dadosLimpos['price_num'] > 0) & 
            (self.dadosLimpos['area'] > 0)
        ]
        
        QuantidadeFinal = len(self.dadosLimpos)
        Removidos = quantidadeInicial - QuantidadeFinal
        
        print(f"Registros iniciais: {quantidadeInicial}")
        print(f"Registros removidos: {Removidos} ({Removidos/quantidadeInicial*100:.1f}%)")
        print(f"Registros finais: {QuantidadeFinal}")
        
        return self.dadosLimpos
    
    def CalculaPrecoM2(self) -> pd.DataFrame:
       
        if self.dadosLimpos is None:
            self.limpaDados()
        
        print("\nCalculando preço por m²...")
        self.dadosLimpos['price_per_m2'] = self.dadosLimpos['price_num'] / self.dadosLimpos['area']
        
        print(f"Preço médio por m²: R$ {self.dadosLimpos['price_per_m2'].mean():.2f}")
        print(f"Preço mediano por m²: R$ {self.dadosLimpos['price_per_m2'].median():.2f}")
        
        return self.dadosLimpos
    
    def group_by_location(self, by='both'):
      if self.dadosLimpos is None or 'price_per_m2' not in self.dadosLimpos.columns:
            self.CalculaPrecoM2()

      print(f"\nAgrupando dados por {by}...")

      if by == 'city':
            group_cols = ['city']
      elif by == 'neighborhood':
            group_cols = ['neighborhood']
      else:  # both
            group_cols = ['city', 'neighborhood']

      df_temp = self.dadosLimpos.dropna(subset=group_cols)

      grouped = df_temp.groupby(group_cols).agg({
            'price_per_m2': ['mean', 'median', 'std', 'min', 'max', 'count'],
            'price_num': ['mean', 'median'],
            'area': ['mean', 'median']
      }).round(2)

      grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
      grouped = grouped.reset_index()
      grouped = grouped.sort_values('price_per_m2_mean', ascending=False)

      return grouped

    
    def CriaVisualizacao(self, 
                           chart_type: Literal['bar', 'boxplot', 'scatter'] = 'boxplot',
                           by: Literal['city', 'neighborhood'] = 'city',
                           output_path: str = 'output/graficos',
                           filename: str = None) -> str:
          
        if self.dadosLimpos is None or 'price_per_m2' not in self.dadosLimpos.columns:
            self.CalculaPrecoM2()
        
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Remove outliers pra melhorar a analise estatística.
        dados_plot = self.dadosLimpos[
            (self.dadosLimpos['price_per_m2'] < self.dadosLimpos['price_per_m2'].quantile(0.99)) &
            (self.dadosLimpos['price_per_m2'] > self.dadosLimpos['price_per_m2'].quantile(0.01))
        ].copy()
        
        # Remove registros com localização nula
        dados_plot = dados_plot.dropna(subset=[by])
        
        # Gera nome do arquivo se não fornecido
        if filename is None:
            filename = f'{chart_type}_{by}_price_per_m2'
        
        filepath = Path(output_path) / f'{filename}.png'
        
        print(f"\nGerando gráfico {chart_type} por {by}...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        if chart_type == 'bar':
            grouped = dados_plot.groupby(by)['price_per_m2'].mean().sort_values(ascending=False)
            
            bars = ax.bar(range(len(grouped)), grouped.values, color='steelblue', alpha=0.8)
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            ax.set_ylabel('Preço Médio por m² (R$)', fontsize=12)
            ax.set_xlabel(by.title(), fontsize=12)
            ax.set_title(f'Preço Médio por m² por {by.title()}', fontsize=14, fontweight='bold')
            
            # Adiciona valores nas barras
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'R$ {height:.0f}',
                       ha='center', va='bottom', fontsize=9)
            
            ax.grid(axis='y', alpha=0.3)
            
        elif chart_type == 'boxplot':
            order = dados_plot.groupby(by)['price_per_m2'].median().sort_values(ascending=False).index
            
            sns.boxplot(data=dados_plot, x=by, y='price_per_m2', order=order, 
                       palette='Set2', ax=ax)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_ylabel('Preço por m² (R$)', fontsize=12)
            ax.set_xlabel(by.title(), fontsize=12)
            ax.set_title(f'Distribuição de Preço por m² por {by.title()}', 
                        fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
        elif chart_type == 'scatter':
            # Scatter plot: área vs preço, colorido por localização
            locations = dados_plot[by].unique()
            colors = sns.color_palette('husl', len(locations))
            
            for i, location in enumerate(locations):
                dados_loc = dados_plot[dados_plot[by] == location]
                ax.scatter(dados_loc['area'], dados_loc['price_num'], 
                          label=location, alpha=0.6, s=50, color=colors[i])
            
            ax.set_xlabel('Área (m²)', fontsize=12)
            ax.set_ylabel('Preço (R$)', fontsize=12)
            ax.set_title(f'Relação Área vs Preço por {by.title()}', 
                        fontsize=14, fontweight='bold')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
            ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráfico salvo em: {filepath}")
        
        return str(filepath)
    
    def criaTotalsVisualizacoes(self, output_path: str = 'output/graficos') -> list[str]:
        
        saved_files = []
        
        for chart_type in ['bar', 'boxplot', 'scatter']:
            try:
                filepath = self.CriaVisualizacao(
                    chart_type=chart_type,
                    by='city',
                    output_path=output_path
                )
                saved_files.append(filepath)
            except Exception as e:
                print(f"Erro ao criar gráfico {chart_type} por cidade: {e}")
        
        # Gráficos por bairro (apenas bar e boxplot, scatter fica muito poluído)
        for chart_type in ['bar', 'boxplot']:
            try:
                filepath = self.CriaVisualizacao(
                    chart_type=chart_type,
                    by='neighborhood',
                    output_path=output_path
                )
                saved_files.append(filepath)
            except Exception as e:
                print(f"Erro ao criar gráfico {chart_type} por bairro: {e}")
        
        print(f"\nTotal de gráficos criados: {len(saved_files)}")
        return saved_files
    
    def GerarRelatorio(self, output_path: str = 'output') -> str:
        
        if self.dadosLimpos is None or 'price_per_m2' not in self.dadosLimpos.columns:
            self.calculate_price_per_m2()
        
        Path(output_path).mkdir(parents=True, exist_ok=True)
        filepath = Path(output_path) / 'relatorio_analise.txt'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE DE IMÓVEIS\n")
            f.write("=" * 80 + "\n\n")
            
            # Estatísticas gerais
            f.write("ESTATÍSTICAS GERAIS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total de imóveis analisados: {len(self.dadosLimpos)}\n")
            f.write(f"Preço médio: R$ {self.dadosLimpos['price_num'].mean():.2f}\n")
            f.write(f"Preço mediano: R$ {self.dadosLimpos['price_num'].median():.2f}\n")
            f.write(f"Área média: {self.dadosLimpos['area'].mean():.2f} m²\n")
            f.write(f"Área mediana: {self.dadosLimpos['area'].median():.2f} m²\n")
            f.write(f"Preço médio por m²: R$ {self.dadosLimpos['price_per_m2'].mean():.2f}\n")
            f.write(f"Preço mediano por m²: R$ {self.dadosLimpos['price_per_m2'].median():.2f}\n\n")
            
            # Top 10 cidades mais caras
            f.write("TOP 10 CIDADES - MAIOR PREÇO POR M²\n")
            f.write("-" * 80 + "\n")
            top_cities = self.dadosLimpos.groupby('city')['price_per_m2'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)
            for i, (city, row) in enumerate(top_cities.iterrows(), 1):
                f.write(f"{i:2d}. {city:30s} - R$ {row['mean']:8.2f}/m² ({int(row['count'])} imóveis)\n")
            
            f.write("\n")
            
            # Top 10 bairros mais caros
            f.write("TOP 10 BAIRROS - MAIOR PREÇO POR M²\n")
            f.write("-" * 80 + "\n")
            dados_temp = self.dadosLimpos.dropna(subset=['neighborhood'])
            top_neighborhoods = dados_temp.groupby('neighborhood')['price_per_m2'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(10)
            for i, (neighborhood, row) in enumerate(top_neighborhoods.iterrows(), 1):
                f.write(f"{i:2d}. {neighborhood:30s} - R$ {row['mean']:8.2f}/m² ({int(row['count'])} imóveis)\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
        
        print(f"\nRelatório salvo em: {filepath}")
        return str(filepath)