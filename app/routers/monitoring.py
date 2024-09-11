from clickhouse_connect.driver.client import Client
from crud import get_db_client
from crud.analyzer import get_all_analyzers
from crud.data_handler import (
    add_new_request,
    add_new_response,
    get_analyzer_results_by_api_key,
    get_request_analyzers_results,
)
from crud.product import update_mode
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from models.monitoring_data import AnalysisResults
from models.product import Product
from routers import verify_api_key
from schemas.monitoring import (
    ChangeModeRequest,
    MonitoringInputRequest,
    MonitoringInputResponse,
    MonitoringOutputRequest,
    MonitoringOutputResponse,
)
from services.analyzers_service import analyzers_service

monitoring_router = APIRouter(prefix="/monitoring")


@monitoring_router.get("/auth", status_code=status.HTTP_200_OK)
async def product_auth(product: Product = Depends(verify_api_key)):
    pass


@monitoring_router.post(
    "/input",
    status_code=status.HTTP_200_OK,
    response_model=MonitoringInputResponse,
)
async def input(
    input_request: MonitoringInputRequest,
    background_tasks: BackgroundTasks,
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    request = add_new_request(
        client=client,
        product=product,
        user_id=input_request.user_id,
        input_text=input_request.input_text,
    )
    analyzers = get_all_analyzers(client=client, type="input")

    print("ANALYZERS: ", analyzers)

    if len(analyzers) > 0:
        background_tasks.add_task(analyzers_service.send_input_async, product, request, analyzers)

    response = MonitoringInputResponse(mode=product.mode, request_id=request.request_id)

    return response


@monitoring_router.post(
    "/output",
    status_code=status.HTTP_200_OK,
    response_model=MonitoringOutputResponse,
)
async def output(
    output_request: MonitoringOutputRequest,
    background_tasks: BackgroundTasks,
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    response = add_new_response(
        client=client,
        request_id=output_request.request_id,
        output_text=output_request.output_text,
    )
    analyzers = get_all_analyzers(client=client, type="output")

    print("ANALYZERS: ", analyzers)

    final_reject_flg = None

    if len(analyzers) > 0:
        if product.mode == "sync":
            monitoring_answer = analyzers_service.send_output(product, response, analyzers)

            request_analyzers_results = get_request_analyzers_results(
                client=client,
                request_id=output_request.request_id,
            )
            request_reject_flg = any([result.reject_flg for result in request_analyzers_results])

            final_reject_flg = monitoring_answer.reject_flg or request_reject_flg
        elif product.mode == "async":
            background_tasks.add_task(analyzers_service.send_output_async, product, response, analyzers)

    response = MonitoringOutputResponse(reject_flg=final_reject_flg)
    return response


@monitoring_router.post("/change_mode", status_code=status.HTTP_200_OK)
async def change_mode(
    mode_request: ChangeModeRequest,
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    if mode_request.mode not in ["sync", "async"]:
        raise HTTPException(status_code=400, detail="Mode could be only: sync, async.")

    update_mode(client=client, api_key=product.api_key, mode=mode_request.mode)


@monitoring_router.get(
    "/data",
    status_code=status.HTTP_200_OK,
    response_model=AnalysisResults,
)
async def get_data(
    client: Client = Depends(get_db_client),
    product: Product = Depends(verify_api_key),
):
    all_monitoring_data = get_analyzer_results_by_api_key(client, product.api_key)
    return all_monitoring_data
