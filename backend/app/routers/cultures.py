from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def listar_culturas():
    cultures = {
        2692: "Arroz (em casca)",
        2696: "Cana-de-açúcar",
        2702: "Feijão (em grão)",
        2711: "Milho (em grão)",
        2713: "Soja (em grão)",
        2716: "Trigo (em grão)"}

    return {"culturas": cultures}
