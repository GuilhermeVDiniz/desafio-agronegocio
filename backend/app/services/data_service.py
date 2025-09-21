import pandas as pd
import sidrapy
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)



def validate_parameters(years: List[str], variaveis: List[str], products: List[str]) -> Dict[str, Any]:
    errors = []

    # Validar anos
    valid_years = []
    for year in years:
        if re.match(r'^\d{4}$', str(year)) and 2021 <= int(year) <= 2025:
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

    # Validar produtos (códigos SIDRA começam com 26xx, 27xx, etc)
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
        max_retries: int = 3
) -> pd.DataFrame:

    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Tentativa {attempt + 1}/{max_retries}")
            logger.info(f"📋 Parâmetros: table={table_id}, level={territorial_level}, region={region_code}")
            logger.info(f"📊 Anos: {years}, Variáveis: {variaveis}, Produtos: {products}")

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
                "classifications": {"81": ",".join(products)},  # C81 para lavouras temporárias
                "header": "n",  # Sem cabeçalho de metadados
                "format": "list"  # Formato lista (mais confiável)
            }

            logger.info(f"🔗 Fazendo requisição com parâmetros: {params}")

            # Fazer requisição
            raw_data = sidrapy.get_table(**params)

            if not raw_data:
                logger.warning("⚠️ SIDRA retornou dados vazios")
                if attempt < max_retries - 1:
                    continue
                return pd.DataFrame()

            logger.info(f"✅ Dados recebidos: {len(raw_data)} linhas")

            # Processar dados
            if len(raw_data) < 2:
                logger.warning("⚠️ Dados insuficientes")
                return pd.DataFrame()

            # Primeira linha são os cabeçalhos
            headers = raw_data[0]
            data_rows = raw_data[1:]

            logger.info(f"📋 Cabeçalhos: {headers}")

            # Criar DataFrame
            df = pd.DataFrame(data_rows, columns=headers)

            if df.empty:
                logger.warning("⚠️ DataFrame vazio após criação")
                return pd.DataFrame()

            logger.info(f"📊 DataFrame inicial: {df.shape}")
            logger.info(f"🔍 Colunas: {df.columns.tolist()}")

            # Processar colunas (mapear nomes)
            df_processed = process_sidra_columns(df)

            if df_processed.empty:
                logger.warning("⚠️ DataFrame vazio após processamento")
                return pd.DataFrame()

            logger.info(f"✅ Processamento concluído: {len(df_processed)} registros")

            return df_processed

        except Exception as e:
            logger.error(f"❌ Erro na tentativa {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                logger.info("🔄 Tentando novamente...")
                continue
            else:
                logger.error("❌ Todas as tentativas falharam")
                return pd.DataFrame()

    return pd.DataFrame()


def process_sidra_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:
        logger.info("🔄 Iniciando processamento de colunas...")

        if df.empty or not isinstance(df, pd.DataFrame):
            logger.warning("DataFrame vazio ou inválido recebido para processamento.")
            return pd.DataFrame()

        df_clean = df.copy()
        logger.info(f"📋 DataFlame Clean: {df_clean}")

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

        for col in df.columns:
            col_lower = col.lower()
            for exacts, contains, name in rules:
                if col in exacts or any(c in col_lower for c in contains):
                    column_mapping[col] = name
                    break

        logger.info(f"📋 Mapeamento de colunas: {column_mapping}")

        # Renomear colunas mapeadas
        if column_mapping:
            df_clean = df_clean.rename(columns=column_mapping)

        # Processar informações do município (se a coluna existir)
        # Agora, 'municipio_completo' deve conter o valor de D1N
        if 'municipio_completo' in df_clean.columns:
            logger.info(f"📊 DataFrame antes de extract_municipality_data: {df_clean.shape}")
            logger.info(f"🔍 Colunas antes de extract_municipality_data: {df_clean.columns.tolist()}")
            df_clean = extract_municipality_data(df_clean)
            logger.info(f"📊 DataFrame após extract_municipality_data: {df_clean.shape}")
            logger.info(f"🔍 Colunas após extract_municipality_data: {df_clean.columns.tolist()}")

        # Converter tipos de dados
        df_clean = convert_data_types(df_clean)

        # Limpar dados inválidos
        df_clean = clean_invalid_data(df_clean)

        logger.info(f"✅ Colunas processadas: {df_clean.columns.tolist()}")
        logger.info(f"📊 Registros após limpeza: {len(df_clean)}")

        return df_clean

    except:
        return df


def extract_municipality_data(df: pd.DataFrame) -> pd.DataFrame:
    df_result = df.copy()

    if 'municipio_completo' not in df_result.columns:
        logger.warning("⚠️ Coluna 'municipio_completo' não encontrada no DataFrame para extração.")
        return df_result

    logger.info("Iniciando extração de dados de município.")
    logger.info(f"Tipo de 'municipio_completo': {type(df_result['municipio_completo'])}")
    logger.info(f"Primeiros valores:\n{df_result['municipio_completo'].head()}")

    # Extrai nome e código IBGE do texto
    extracted = df_result['municipio_completo'].astype(str).str.extract(
        r'^(.*?)(?:\s*\((\d+)\))?\s*$',
        expand=True
    )

    logger.info(f"Resultado de str.extract():\n{extracted.head()}")

    # Nome do município
    df_result['municipio_nome'] = extracted[0].fillna(df_result['municipio_completo'])

    # Código IBGE (se não estiver preenchido)
    if 'municipio_codigo_ibge' not in df_result.columns:
        df_result['municipio_codigo_ibge'] = None

    if not extracted.empty and extracted.shape[1] > 1:
        ibge_codes = extracted[1]
        mask_no_ibge_code = df_result['municipio_codigo_ibge'].isna()
        df_result.loc[mask_no_ibge_code, 'municipio_codigo_ibge'] = ibge_codes.loc[mask_no_ibge_code]

    # Preenche com D1C se ainda houver NAs
    if 'D1C' in df.columns:
        df_result['municipio_codigo_ibge'] = df_result['municipio_codigo_ibge'].fillna(df['D1C'])

    # Remove coluna original
    df_result = df_result.drop(columns=['municipio_completo'], errors='ignore')

    logger.info(f"Colunas finais: {df_result.columns.tolist()}")
    logger.info(f"Primeiros valores de 'municipio_nome':\n{df_result['municipio_nome'].head()}")
    logger.info(f"Primeiros valores de 'municipio_codigo_ibge':\n{df_result['municipio_codigo_ibge'].head()}")

    return df_result


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Converte tipos de dados"""
    df_result = df.copy()
    logger.info("Iniciando conversão de tipos de dados.")

    # Converter ano
    if 'ano' in df_result.columns:
        df_result['ano'] = pd.to_numeric(df_result['ano'], errors='coerce')
        logger.info(f"Coluna 'ano' convertida. Primeiros valores:\n{df_result['ano'].head()}")
    elif 'D2C' in df_result.columns:
        df_result['ano'] = pd.to_numeric(df_result['D2C'], errors='coerce')
        logger.info(f"Coluna 'D2C' convertida como 'ano'. Primeiros valores:\n{df_result['ano'].head()}")

    # Converter valor
    if 'valor' in df_result.columns:
        df_result['valor'] = df_result['valor'].replace('-', pd.NA)
        df_result['valor'] = pd.to_numeric(df_result['valor'], errors='coerce')
        logger.info(f"Coluna 'valor' convertida. Primeiros valores:\n{df_result['valor'].head()}")
    elif 'V' in df_result.columns:
        df_result['valor'] = df_result['V'].replace('-', pd.NA)
        df_result['valor'] = pd.to_numeric(df_result['valor'], errors='coerce')
        logger.info(f"Coluna 'V' convertida como 'valor'. Primeiros valores:\n{df_result['valor'].head()}")

    # Converter códigos
    for col in ['municipio_codigo_ibge', 'produto_codigo', 'nivel_territorial_codigo']:
        if col in df_result.columns:
            df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
            logger.info(f"Coluna '{col}' convertida. Primeiros valores:\n{df_result[col].head()}")

    # Limpar strings
    string_columns = ['produto_nome', 'variavel_nome', 'municipio_nome', 'unidade', 'nivel_territorial_nome']
    for col in string_columns:
        if col in df_result.columns:
            df_result[col] = df_result[col].astype(str).str.strip()
            logger.info(f"Coluna '{col}' limpa. Primeiros valores:\n{df_result[col].head()}")

    logger.info("Finalizando conversão de tipos de dados.")
    return df_result


def clean_invalid_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove dados inválidos"""
    df_result = df.copy()
    logger.info("Iniciando limpeza de dados inválidos.")
    logger.info(f"Registros antes da limpeza: {len(df_result)}")

    # Remover valores nulos essenciais
    essential_cols = ['valor', 'ano']
    for col in essential_cols:
        if col in df_result.columns:
            initial_len = len(df_result)
            df_result = df_result.dropna(subset=[col])
            if len(df_result) < initial_len:
                logger.info(f"Removidos {initial_len - len(df_result)} registros com NA na coluna '{col}'.")

    # Remover valores zero ou negativos (após conversão para numérico)
    if 'valor' in df_result.columns:
        initial_len = len(df_result)
        df_result = df_result[df_result['valor'] > 0]
        if len(df_result) < initial_len:
            logger.info(f"Removidos {initial_len - len(df_result)} registros com 'valor' <= 0.")

    # Remover municípios sem código IBGE (se a coluna existir e for relevante)
    if 'municipio_codigo_ibge' in df_result.columns:
        initial_len = len(df_result)
        df_result = df_result.dropna(subset=['municipio_codigo_ibge'])
        if len(df_result) < initial_len:
            logger.info(f"Removidos {initial_len - len(df_result)} registros com NA na coluna 'municipio_codigo_ibge'.")

    logger.info(f"Registros após limpeza: {len(df_result)}")
    logger.info("Finalizando limpeza de dados inválidos.")
    return df_result
