import pandas as pd
import sidrapy
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


def validate_parameters(years: List[str], variaveis: List[str], products: List[str]) -> Dict[str, Any]:
    errors = []

    valid_years = []
    for year in years:
        if re.match(r'^\d{4}$', str(year)) and 2021 <= int(year) < 2025:
            valid_years.append(str(year))
        elif year.lower() == 'last':
            valid_years.append('last')
        else:
            errors.append(f"Ano inválido: {year}")

    # Validar variáveis
    valid_vars = ["109", "214", "215", "216", "112"]
    invalid_vars = [v for v in variaveis if v not in valid_vars]
    if invalid_vars:
        errors.append(f"Variáveis inválidas: {invalid_vars}")

    # Validar produtos (códigos SIDRA )
    invalid_products = []
    for product in products:
        if not re.match(r'^\d{4}$', str(product)):
            invalid_products.append(product)

    if invalid_products:
        errors.append(f"Códigos de produtos inválidos: {invalid_products}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "valid_years": valid_years,
        "valid_vars": [v for v in variaveis if v in valid_vars],
        "valid_products": [p for p in products if p not in invalid_products]
    }


def fetch_and_process_production_data(
        years: List[str] = ["last"],
        variaveis: List[str] = ["216"],
        products: List[str] = ["2702", "2704", "2713"],
        table_id: str = "1612",
        territorial_level: str = "8",
        region_code: str = "all",
        max_retries: int = 3) -> pd.DataFrame:
    for attempt in range(max_retries):
        try:

            # Preparar período
            if len(years) == 1 and years[0] == "last":
                period = "last"
            else:
                period = ",".join(years)

            # Preparar parâmetros SIDRA
            params = {
                "table_code": table_id,
                "territorial_level": territorial_level,
                "ibge_territorial_code": region_code,
                "variable": ",".join(variaveis),
                "period": period,
                "classifications": {"81": ",".join(products)},
                "header": "n",
                "format": "list"
            }

            raw_data = sidrapy.get_table(**params)

            if not raw_data:
                logger.warning("SIDRA retornou dados vazios")
                if attempt < max_retries - 1:
                    continue
                return pd.DataFrame()

            if len(raw_data) < 2:
                return pd.DataFrame()

            # Primeira linha são os cabeçalhos
            headers = raw_data[0]
            data_rows = raw_data[1:]
            df = pd.DataFrame(data_rows, columns=headers)

            if df.empty:
                logger.warning("DataFrame vazio")
                return pd.DataFrame()

            df_processed = process_sidra_columns(df)

            if df_processed.empty:
                return pd.DataFrame()

            return df_processed

        except Exception as e:
            # faz 3 tentativa de busca
            if attempt < max_retries - 1:
                continue
            else:
                logger.error(f"Todas as tentativas falharam: {str(e)}")
                return pd.DataFrame()

    return pd.DataFrame()


def process_sidra_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if df.empty or not isinstance(df, pd.DataFrame):
            logger.warning("DataFrame vazio ou inválido.")
            return pd.DataFrame()

        df_clean = df.copy()
        logger.info(f"DataFlame Clean: {df_clean}")

        # Mapear colunas mais comuns do SIDRA
        column_mapping = {}

        rules = [
            (['D1N'], ['município', 'territorial'], 'municipio_completo'),
            (['D1C'], [], 'municipio_codigo_ibge'),
            (['D2C', 'D2N'], ['ano'], 'ano'),
            (['D3N'], ['variável'], 'variavel_nome'),
            (['D4N'], ['produto'], 'produto_nome'),
            (['D4C'], [], 'produto_codigo'),
            (['V'], ['valor'], 'valor'),
            (['MN'], ['unidade'], 'unidade'),
            (['NN'], [], 'nivel_territorial_nome'),
            (['NC'], [], 'nivel_territorial_codigo'),
        ]

        for column in df.columns:
            col_lower = column.lower()
            for exacts, contains, name in rules:
                if column in exacts or any(c in col_lower for c in contains):
                    column_mapping[column] = name
                    break

        # Renomear colunas mapeadas
        if column_mapping:
            df_clean = df_clean.rename(columns=column_mapping)

        if 'municipio_completo' in df_clean.columns:
            df_clean = extract_municipality_data(df_clean)

        # Converter tipos de dados
        df_clean = convert_data_types(df_clean)

        # Limpar dados inválidos
        df_clean = clean_invalid_data(df_clean)

        return df_clean

    except:
        return df


def extract_municipality_data(df: pd.DataFrame) -> pd.DataFrame:
    df_result = df.copy()

    if 'municipio_completo' not in df_result.columns:
        return df_result

    # Extrai nome e código IBGE do texto
    extracted = df_result['municipio_completo'].astype(str).str.extract(
        r'^(.*?)(?:\s*\((\d+)\))?\s*$',
        expand=True
    )
    df_result['municipio_nome'] = extracted[0].fillna(df_result['municipio_completo'])

    if 'municipio_codigo_ibge' not in df_result.columns:
        df_result['municipio_codigo_ibge'] = None

    if not extracted.empty and extracted.shape[1] > 1:
        ibge_codes = extracted[1]
        mask_no_ibge_code = df_result['municipio_codigo_ibge'].isna()
        df_result.loc[mask_no_ibge_code, 'municipio_codigo_ibge'] = ibge_codes.loc[mask_no_ibge_code]

    # Preenche com D1C se ainda houver NAs
    if 'D1C' in df.columns:
        df_result['municipio_codigo_ibge'] = df_result['municipio_codigo_ibge'].fillna(df['D1C'])


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Converte tipos de dados"""
    df_result = df.copy()

    # Converter ano
    if 'ano' in df_result.columns:
        df_result['ano'] = pd.to_numeric(df_result['ano'], errors='coerce')
    elif 'D2C' in df_result.columns:
        df_result['ano'] = pd.to_numeric(df_result['D2C'], errors='coerce')

    # Converter valor
    if 'valor' in df_result.columns:
        df_result['valor'] = df_result['valor'].replace('-', pd.NA)
        df_result['valor'] = pd.to_numeric(df_result['valor'], errors='coerce')
    elif 'V' in df_result.columns:
        df_result['valor'] = df_result['V'].replace('-', pd.NA)
        df_result['valor'] = pd.to_numeric(df_result['valor'], errors='coerce')

    # Converter códigos
    for col in ['municipio_codigo_ibge', 'produto_codigo', 'nivel_territorial_codigo']:
        if col in df_result.columns:
            df_result[col] = pd.to_numeric(df_result[col], errors='coerce')

    # Limpar strings
    string_columns = ['produto_nome', 'variavel_nome', 'municipio_nome', 'unidade', 'nivel_territorial_nome']
    for col in string_columns:
        if col in df_result.columns:
            df_result[col] = df_result[col].astype(str).str.strip()

    return df_result


def clean_invalid_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove dados inválidos"""
    df_result = df.copy()

    # Remover valores nulos essenciais
    essential_cols = ['valor', 'ano']
    for col in essential_cols:
        if col in df_result.columns:
            df_result = df_result.dropna(subset=[col])
    # Remover valores zero ou negativos (após conversão para numérico)
    if 'valor' in df_result.columns:
        df_result = df_result[df_result['valor'] > 0]

    # Remover municípios sem código IBGE (se a coluna existir e for relevante)
    if 'municipio_codigo_ibge' in df_result.columns:
        df_result = df_result.dropna(subset=['municipio_codigo_ibge'])

    return df_result
