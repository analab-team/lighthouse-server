import requests
from clickhouse_connect.driver.client import Client
from crud import get_db_client
from crud.analyzer import get_all_analyzers, get_analyzer
from fastapi import APIRouter, Depends, HTTPException, status
from models.product import Product
from pydantic import ValidationError
from routers import verify_api_key
from schemas.vault import AddAnalyzerRequest, GetAnalyzersResponse, GetVaultExample
from services.vault_service import (
    generate_pydantic_model_from_schema,
    get_pydantic_model_from_schema,
    get_vault_example_schema,
)

vault_router = APIRouter(prefix="/vault")


@vault_router.get(
    "/get_all_analyzers",
    status_code=status.HTTP_200_OK,
    response_model=GetAnalyzersResponse,
)
async def all_analyzers(client: Client = Depends(get_db_client)):
    input_analyzers = [analyzer.analyzer_name for analyzer in get_all_analyzers(client=client, type="input")]
    output_analyzers = [analyzer.analyzer_name for analyzer in get_all_analyzers(client=client, type="output")]
    response = GetAnalyzersResponse(input=input_analyzers, output=output_analyzers)
    return response


@vault_router.get(
    "/example",
    status_code=status.HTTP_200_OK,
    response_model=GetVaultExample,
)
async def vault_example(
    analyzer_name: str,
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    analyzer = get_analyzer(client=client, analyzer_name=analyzer_name)
    if analyzer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No analyzer with name: {analyzer_name}",
        )

    schema = get_vault_example_schema(analyzer=analyzer, api_key=product.api_key)
    vault_model = generate_pydantic_model_from_schema(schema)

    input_fields = {name: str(info) for name, info in vault_model.model_fields.items()}

    response = GetVaultExample(fields=input_fields)

    return response


@vault_router.post("/add", status_code=status.HTTP_200_OK)
async def add_vault(
    new_vault: AddAnalyzerRequest,
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    analyzer = get_analyzer(client=client, analyzer_name=new_vault.analyzer_name)
    if analyzer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No analyzer with name: {new_vault.analyzer_name}",
        )

    schema = get_vault_example_schema(analyzer=analyzer, api_key=product.api_key)
    try:
        vault_model = get_pydantic_model_from_schema(schema, new_vault.vault).model_dump()
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wrong vault model: {e}. Use /vault/example method.",
        )

    endpoint = f"{analyzer.host}:{analyzer.port}/manager/add_vault"
    response = requests.post(endpoint, json=vault_model, headers={"api_key": product.api_key})

    if response.status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Can't add your vault to the {new_vault.analyzer_name} analyzer.",
        )
