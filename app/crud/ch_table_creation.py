create_tables_queries = [
    """
    CREATE TABLE IF NOT EXISTS products (
        product_id UUID DEFAULT generateUUIDv4(), -- PK
        product_name String,
        api_key String,
        mode String
    ) ENGINE = MergeTree()
    ORDER BY product_id;
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id String, -- PK
        username String
    ) ENGINE = MergeTree()
    ORDER BY user_id;
    """,
    """
    CREATE TABLE IF NOT EXISTS requests (
        request_id UUID DEFAULT generateUUIDv4(), -- PK
        user_id String, -- FK from users
        timestamp DateTime,
        session_id String,
        product_id UUID, -- FK from products
        input_text String
    ) ENGINE = MergeTree()
    ORDER BY request_id;
    """,
    """
    CREATE TABLE IF NOT EXISTS response (
        response_id UUID DEFAULT generateUUIDv4(), -- PK
        request_id UUID, -- FK from requests
        timestamp DateTime,
        output_text String
    ) ENGINE = MergeTree()
    ORDER BY response_id;
    """,
    """
    CREATE TABLE IF NOT EXISTS analyzers (
        analyzer_name String,
        description String,
        host String,
        port INTEGER,
        endpoint String,
        type String,
    ) ENGINE = MergeTree()
    PRIMARY KEY analyzer_name
    ORDER BY analyzer_name;
    """,
    """
    CREATE TABLE IF NOT EXISTS request_analysis_results (
        result_id UUID DEFAULT generateUUIDv4(), -- PK
        request_id UUID, -- FK from requests
        analyzer_name String, -- FK from analyzers
        metric Float32,
        reject_flg BOOL,
        reasons String,
    ) ENGINE = MergeTree()
    ORDER BY result_id;
    """,
    """
    CREATE TABLE IF NOT EXISTS response_analysis_results (
        result_id UUID DEFAULT generateUUIDv4(), -- PK
        response_id UUID, -- FK from requests
        analyzer_name String, -- FK from analyzers
        metric Float32,
        reject_flg BOOL,
        reasons String,
    ) ENGINE = MergeTree()
    ORDER BY result_id;
    """,
]
