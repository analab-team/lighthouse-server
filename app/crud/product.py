from uuid import UUID

from clickhouse_connect.driver.client import Client
from crud.exceptions import ProductAlreadyExists
from models.product import Product, ProductCreation


def get_product_by_name(client: Client, product_name: str) -> Product | None:
    stmt = "SELECT * FROM products WHERE product_name=%(product_name)s"
    try:
        row = client.query(stmt, parameters={"product_name": product_name}).first_item
    except IndexError:
        return None
    product = Product(**row)
    return product


def get_product(client: Client, api_key: UUID) -> Product | None:
    stmt = "SELECT * FROM products WHERE api_key=%(api_key)s"
    try:
        row = client.query(stmt, parameters={"api_key": api_key}).first_item
    except IndexError:
        return None
    product = Product(**row)
    return product


def add_new_product(client: Client, product_name: str) -> ProductCreation:
    stmt = """
    INSERT INTO products (product_name, api_key, mode)
    VALUES (%(product_name)s, %(api_key)s, %(mode)s)
    """
    if get_product_by_name(client=client, product_name=product_name) is not None:
        raise ProductAlreadyExists

    product = ProductCreation(product_name=product_name)
    client.query(stmt, parameters=product.model_dump())

    return product


def update_mode(client: Client, api_key: str, mode: str) -> None:
    stmt = """
    ALTER TABLE products
    UPDATE mode=%(mode)s
    WHERE api_key=%(api_key)s
    """
    client.query(stmt, parameters={"mode": mode, "api_key": api_key})
