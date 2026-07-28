import os

import pytest
from dotenv import load_dotenv

from charissa.data.postgres_source import load_query
from charissa.executor.docker_executor import DockerExecutor

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set",
)


def test_load_query_against_real_database():
    executor = DockerExecutor()
    try:
        result = load_query(executor, os.environ["DATABASE_URL"], "SELECT 1 AS x", "result")
        assert result["traceback"] == ""
        assert "1" in result["stdout"]
    finally:
        executor.close()
