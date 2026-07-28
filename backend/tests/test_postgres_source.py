import time

import pytest
import sqlalchemy

from charissa.data.postgres_source import load_query
from charissa.executor.docker_executor import DockerExecutor, _docker_client


def _wait_for_postgres(url: str, retries: int = 50):
    for _ in range(retries):
        try:
            engine = sqlalchemy.create_engine(url)
            with engine.connect():
                engine.dispose()
                return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("postgres did not become ready")


@pytest.fixture(scope="module")
def postgres_url():
    client = _docker_client()
    container = client.containers.run(
        "postgres:16-alpine",
        detach=True,
        environment={"POSTGRES_PASSWORD": "postgres", "POSTGRES_DB": "testdb"},
        ports={"5432/tcp": None},
    )
    try:
        container.reload()
        port = container.ports["5432/tcp"][0]["HostPort"]
        url = f"postgresql+psycopg://postgres:postgres@localhost:{port}/testdb"
        _wait_for_postgres(url)
        yield url
    finally:
        container.stop(timeout=1)
        container.remove()


@pytest.fixture
def executor():
    ex = DockerExecutor()
    yield ex
    ex.close()


def test_load_query_creates_dataframe(postgres_url, executor):
    engine = sqlalchemy.create_engine(postgres_url)
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("CREATE TABLE products (name text, price int)"))
        conn.execute(sqlalchemy.text("INSERT INTO products VALUES ('apple', 3), ('banana', 5)"))
    engine.dispose()

    result = load_query(executor, postgres_url, "SELECT * FROM products", "products")

    assert result["traceback"] == ""
    assert "apple" in result["stdout"]

    followup = executor.run("print(len(products))")
    assert followup["stdout"].strip() == "2"
