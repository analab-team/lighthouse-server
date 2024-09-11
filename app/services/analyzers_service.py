import asyncio
from typing import List

import httpx
import requests
from fastapi import HTTPException, status
from models.analyzer import Analyzer
from models.product import Product
from models.request import Request
from models.response import Response
from schemas.analyzers import InputRequest, OutputRequest, OutputResponse


class AnalyzersService:
    async def send_input_async(self, product: Product, request: Request, input_analyzers: List[Analyzer]):
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = []
            for analyzer in input_analyzers:
                endpoint = f"{analyzer.host}:{analyzer.port}/{analyzer.endpoint}"
                print(endpoint)
                try:
                    input_request = InputRequest(
                        request_id=request.request_id,
                        input_text=request.input_text,
                        analyzer_name=analyzer.analyzer_name,
                    )
                    print(input_request.model_dump())
                    tasks.append(
                        client.post(
                            url=endpoint,
                            json=input_request.model_dump(),
                            headers={"api_key": product.api_key},
                        )
                    )
                except httpx.RequestError as exc:
                    print(f"Error sending request to {endpoint}: {exc}")
                except Exception as e:
                    print(f"Some other problem: {e.with_traceback()}")
            await asyncio.gather(*tasks)

    async def send_output_async(self, product: Product, response: Response, output_analyzers: List[Analyzer]):
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = []
            for analyzer in output_analyzers:
                endpoint = f"{analyzer.host}:{analyzer.port}/{analyzer.endpoint}"
                try:
                    output_request = OutputRequest(
                        response_id=response.response_id,
                        output_text=response.output_text,
                        analyzer_name=analyzer.analyzer_name,
                    )
                    task = client.post(
                        url=endpoint,
                        json=output_request.model_dump(),
                        headers={"api_key": product.api_key},
                    )
                    tasks.append(task)
                except httpx.RequestError as exc:
                    print(f"Ошибка при отправке запроса к {endpoint}: {exc}")
            return await asyncio.gather(*tasks)

    def send_output(self, product: Product, response: Response, output_analyzers: List[Analyzer]) -> OutputResponse:
        analyzers_response = list()
        for analyzer in output_analyzers:
            endpoint = f"{analyzer.host}:{analyzer.port}/{analyzer.endpoint}"
            output_request = OutputRequest(
                response_id=response.response_id,
                output_text=response.output_text,
                analyzer_name=analyzer.analyzer_name,
            )
            output_response = requests.post(
                url=endpoint,
                json=output_request.model_dump(),
                headers={"api_key": product.api_key},
            )

            if output_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Can't get output response from {analyzer.analyzer_name} analyzer.",
                )

            output_response_data = OutputResponse(**output_response.json())
            analyzers_response.append(bool(output_response_data.reject_flg))

        final_response = OutputResponse(reject_flg=all(analyzers_response))

        return final_response


analyzers_service = AnalyzersService()
