import pandas as pd
import sidrapy


class DataService:
    def fetch_and_process_production_data(self, id_table):
        try:
            data = sidrapy.get_table(
                table_code="1612",
                territorial_level="6",  # municípios
                ibge_territorial_code="all",
                period="2020",  # ano
                header='n',
                format='list'
            )

            df = pd.DataFrame(data[1:], columns=data[0])

            # Atenção: D2C = período/ano
            columns_to_keep = {
                'NC': 'Nivel_Territorial',
                'NN': 'Nome_Territorial',
                'D2C': 'Ano',
                'D3C': 'Produto_Agricola_Codigo',
                'D3N': 'Produto_Agricola_Nome',
                'V': 'Valor',
                'D4N': 'Tipo_Variavel'
            }

            df_processed = df[columns_to_keep.keys()].rename(columns=columns_to_keep)
            df_processed['Valor'] = pd.to_numeric(df_processed['Valor'], errors='coerce')
            df_processed.dropna(subset=['Valor'], inplace=True)
            df_processed = df_processed[df_processed['Valor'] > 0]

            df_processed['Municipio_ID'] = df_processed['Nome_Territorial'].apply(
                lambda x: x[x.find('(') + 1:x.find(')')] if '(' in x else None
            )
            df_processed['Municipio_Nome'] = df_processed['Nome_Territorial'].apply(
                lambda x: x.split(' (')[0]
            )
            df_processed.dropna(subset=['Municipio_ID'], inplace=True)

            final_columns = ['Ano', 'Municipio_ID', 'Municipio_Nome', 'Produto_Agricola_Nome', 'Valor']
            df_final = df_processed[final_columns]

            return df_final.to_dict(orient='records')

        except Exception as e:
            import traceback
            print("Erro ao buscar/processar dados:", e)
            traceback.print_exc()
            return []


if __name__ == '__main__':
    service = DataService()
    print(service.fetch_and_process_production_data("5459"))
