import pandas as pd
import sqlalchemy

from charissa.executor.docker_executor import DockerExecutor


def _with_psycopg_driver(database_url: str) -> str:
    """Providers like Neon/Supabase hand out plain postgres:// URLs, which
    SQLAlchemy defaults to the psycopg2 dialect. We install psycopg (v3), so
    force that dialect regardless of what the provider gave us."""
    for prefix in ("postgresql://", "postgres://"):
        if database_url.startswith(prefix):
            return "postgresql+psycopg://" + database_url[len(prefix):]
    return database_url


def load_query(executor: DockerExecutor, database_url: str, query: str, varname: str) -> dict:
    """Runs a SQL query against Postgres on the host, then loads the result into
    the sandbox as a DataFrame. The sandbox never sees `database_url` or `query`,
    only the resulting rows.
    """
    engine = sqlalchemy.create_engine(_with_psycopg_driver(database_url))
    try:
        df = pd.read_sql(sqlalchemy.text(query), engine)
    finally:
        engine.dispose()

    csv_bytes = df.to_csv(index=False).encode()
    container_path = executor.upload_bytes(csv_bytes, f"{varname}.csv")
    code = f"import pandas as pd\n{varname} = pd.read_csv('{container_path}')\nprint({varname}.head())"
    return executor.run(code)
