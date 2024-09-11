from clickhouse_connect.driver.client import Client
from crud import get_db_client
from crud.analyzer import add_new_analyzer
from crud.exceptions import AnalyzerAlreadyExists, ProductAlreadyExists
from crud.product import add_new_product
from fastapi import APIRouter, Depends, HTTPException, status
from routers import verify_admin_api_key
from schemas.admin import AddAnalyzerRequest, AddProductResponse

admin_router = APIRouter(prefix="/admin")


@admin_router.get("/auth")
async def admin_auth(admin_verification=Depends(verify_admin_api_key)):
    pass


@admin_router.post(
    "/add_product",
    status_code=status.HTTP_201_CREATED,
    response_model=AddProductResponse,
)
async def add_product(
    product_name: str,
    client: Client = Depends(get_db_client),
    admin_verification=Depends(verify_admin_api_key),
):
    try:
        product = add_new_product(client=client, product_name=product_name)
        return AddProductResponse(api_key=product.api_key)
    except ProductAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with name {product_name} already exists.",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@admin_router.post("/add_analyzer", status_code=status.HTTP_201_CREATED)
async def add_analyzer(
    analyzer: AddAnalyzerRequest,
    client: Client = Depends(get_db_client),
    admin_verification=Depends(verify_admin_api_key),
):
    try:
        add_new_analyzer(client=client, **analyzer.model_dump())
    except AnalyzerAlreadyExists:
        raise HTTPException(status_code=400, detail=f"Analyzer with name {analyzer.analyzer_name} already exists.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
