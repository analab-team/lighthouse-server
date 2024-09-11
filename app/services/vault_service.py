import json
from typing import Any, Dict

import requests
from fastapi import HTTPException, status
from models.analyzer import Analyzer
from pydantic import BaseModel, create_model


def get_vault_example_schema(analyzer: Analyzer, api_key: str) -> dict:
    endpoint = f"{analyzer.host}:{analyzer.port}/manager/vault_example"
    response = requests.get(endpoint, headers={"api_key": api_key})

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Can't get vault schema example from {analyzer.analyzer_name} analyzer",
        )

    response_data = response.json()
    schema = json.loads(response_data["vault_schema"])

    return schema


def generate_pydantic_model_from_schema(schema: dict) -> type[BaseModel]:
    fields = {}
    for field, prop in schema.get("properties", {}).items():
        field_type = str if prop.get("type") == "string" else int
        fields[field] = (field_type, ...)

    GeneratedModel = create_model(schema["title"], **fields)

    return GeneratedModel


def get_pydantic_model_from_schema(schema: dict, data: Dict[str, Any]) -> BaseModel:
    GeneratedModel = generate_pydantic_model_from_schema(schema=schema)
    vault_model = GeneratedModel(**data)

    return vault_model
