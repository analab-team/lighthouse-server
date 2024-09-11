from typing import List

from clickhouse_connect.driver.client import Client
from crud.exceptions import AnalyzerAlreadyExists
from models.analyzer import Analyzer
from pydantic import ValidationError


def add_new_analyzer(
    client: Client,
    analyzer_name: str,
    description: str,
    host: str,
    port: int,
    endpoint: str,
    type: str,
):
    stmt = """
    INSERT INTO analyzers (analyzer_name, description, host, port, endpoint, type)
    VALUES (%(analyzer_name)s, %(description)s, %(host)s, %(port)s, %(endpoint)s, %(type)s)
    """
    analyzer = get_analyzer(client=client, analyzer_name=analyzer_name)
    if analyzer is not None:
        raise AnalyzerAlreadyExists

    analyzer = Analyzer(
        analyzer_name=analyzer_name,
        description=description,
        host=host,
        port=port,
        endpoint=endpoint,
        type=type,
    )
    client.query(stmt, parameters=analyzer.model_dump())


def get_analyzer(client: Client, analyzer_name: str) -> Analyzer | None:
    stmt = "SELECT * FROM analyzers WHERE analyzer_name=%(analyzer_name)s"
    result = client.query(stmt, parameters={"analyzer_name": analyzer_name})
    if len(result.result_set) == 0:
        return None

    try:
        analyzer = Analyzer(**result.first_item)
    except ValidationError:
        return None

    return analyzer


def get_all_analyzers(client: Client, type: str) -> List[Analyzer]:
    stmt = """
    SELECT (analyzer_name, description, host, port, endpoint, type)
    FROM analyzers
    WHERE type=%(type)s
    """
    rows = client.query(stmt, parameters={"type": type}).result_rows

    analyzers = list()
    for row in rows:
        analyzers.append(Analyzer(**row[0]))

    return analyzers
