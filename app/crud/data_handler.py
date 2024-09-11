from typing import List
from uuid import UUID

from clickhouse_connect.driver.client import Client
from crud.product import Product
from models.monitoring_data import AnalysisResults, AnalyzerResult
from models.request import Request, RequestResult
from models.response import Response


def add_new_request(
    client: Client,
    product: Product,
    user_id: str,
    input_text: str,
) -> Request:
    stmt = """
    INSERT INTO requests (request_id, product_id, user_id, timestamp, input_text)
    VALUES (%(request_id)s, %(product_id)s, %(user_id)s, %(timestamp)s, %(input_text)s)
    """
    request = Request(product_id=product.product_id, user_id=user_id, input_text=input_text)
    client.query(stmt, parameters=request.model_dump())

    return request


def add_new_response(
    client: Client,
    request_id: UUID,
    output_text: str,
) -> Response:
    stmt = """
    INSERT INTO response (response_id, request_id, timestamp, output_text)
    VALUES (%(response_id)s, %(request_id)s, %(timestamp)s, %(output_text)s)
    """
    response = Response(output_text=output_text, request_id=request_id)
    client.query(stmt, parameters=response.model_dump())

    return response


def get_request_analyzers_results(client: Client, request_id: UUID) -> List[RequestResult]:
    stmt = """
    SELECT (result_id, request_id, analyzer_name, metric, reject_flg)
    FROM request_analysis_results
    WHERE request_id=%(request_id)s
    """
    rows = client.query(stmt, parameters={"request_id": request_id}).result_rows
    result = list()
    for row in rows:
        result.append(RequestResult(**row[0]))

    return result


def get_analyzer_results_by_api_key(client: Client, api_key: str) -> AnalysisResults:
    product_query = """
        SELECT product_id FROM products WHERE api_key = %(api_key)s
    """
    product_result = client.query(product_query, {"api_key": api_key})
    if not product_result.result_rows:
        raise ValueError(f"Product with api_key {api_key} not found")

    product_id = product_result.result_rows[0][0]

    request_query = """
        SELECT r.request_id, r.timestamp, r.input_text, rar.analyzer_name, rar.metric, rar.reject_flg, rar.reasons
        FROM requests r
        JOIN request_analysis_results rar ON r.request_id = rar.request_id
        WHERE r.product_id = %(product_id)s
    """
    request_results = client.query(request_query, {"product_id": product_id}).result_rows

    response_query = """
        SELECT res.response_id, res.timestamp, res.output_text, ar.analyzer_name, ar.metric, ar.reject_flg, ar.reasons
        FROM response res
        JOIN response_analysis_results ar ON res.response_id = ar.response_id
        JOIN requests r ON res.request_id = r.request_id
        WHERE r.product_id = %(product_id)s
    """
    response_results = client.query(response_query, {"product_id": product_id}).result_rows

    input_results = {}
    output_results = {}

    for row in request_results:
        _, timestamp, input_text, analyzer_name, metric, reject_flg, reasons = row
        if analyzer_name not in input_results:
            input_results[analyzer_name] = []
        input_results[analyzer_name].append(
            AnalyzerResult(
                timestamp=timestamp,
                text=input_text,
                metric=metric,
                reject_flg=reject_flg,
                reasons=reasons,
            )
        )

    for row in response_results:
        _, timestamp, output_text, analyzer_name, metric, reject_flg, reasons = row
        if analyzer_name not in output_results:
            output_results[analyzer_name] = []
        output_results[analyzer_name].append(
            AnalyzerResult(
                timestamp=timestamp,
                text=output_text,
                metric=metric,
                reject_flg=reject_flg,
                reasons=reasons,
            )
        )

    return AnalysisResults(input=input_results, output=output_results)
