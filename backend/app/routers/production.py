from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from app.services.data_service import fetch_and_process_production_data, validate_parameters
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def get_dados(
        ano: str = Query(None, description="Ano de consulta. Ex: '2021 a 2024'"),
        cultura: str = Query(None, description="IDs de cultura. Ex: '2702'"),
):
    """
    Endpoint para buscar dados de produção agrícola do SIDRA-IBGE

    Parâmetros:
    - ano: Ano de consulta (De 2021 a 2024)
    - cultura: Códigos dos produtos agrícolas (padrão: principais culturas)
    - variável: Códigos das variáveis (padrão: 214 - Quantidade produzida)
    - nivel: Nível territorial (padrão: 8 - Mesorregião Geográfica)
    - região: Código da região (padrão: 'all')
    """
    try:
        # Processar parâmetro 'ano'
        years = ano.split(",") if ano else ["2022", "2023"]
        years = [y.strip() for y in years]

        VARIAVEL = ["214"] # Quantidade produzida
        REGIAO = "all"
        NIVEL = "8"

        # Produtos principais
        produtos = cultura.split(",") if cultura else [
            "2702",  # Feijão
            "2704",  # Milho
            "2707",  # Arroz
            "2711",  # Cana-de-açúcar
            "2713",  # Soja
            "2695"  # Algodão
        ]
        produtos = [p.strip() for p in produtos]

        logger.info(f"Consultando SIDRA: anos={years}, produtos={produtos}, variáveis={VARIAVEL}")

        # Validar parâmetros
        validation_result = validate_parameters(years, VARIAVEL, produtos)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Parâmetros inválidos: {validation_result['errors']}"
            )

        # Buscar dados
        df = fetch_and_process_production_data(
            years=years,
            variaveis=VARIAVEL,
            products=produtos,
            territorial_level=NIVEL,
            region_code=REGIAO
        )

        if df.empty:
            return JSONResponse(
                content={
                    "message": "Nenhum dado encontrado para os parâmetros especificados",
                    "parametros": {
                        "anos": years,
                        "produtos": produtos,
                        "variaveis": VARIAVEL
                    }
                },
                status_code=404
            )

        return {
            "dados": df.to_dict(orient="records"),
            "parametros_usados": {
                "anos": years,
                "produtos": produtos,
                "variaveis": VARIAVEL,
                "nivel_territorial": NIVEL,
                "regiao": REGIAO
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na API: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"erro": f"Erro interno: {str(e)}"},
            status_code=500
        )
