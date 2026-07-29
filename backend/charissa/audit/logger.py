import datetime

import sqlalchemy

metadata = sqlalchemy.MetaData()

audit_log_table = sqlalchemy.Table(
    "audit_log",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("session_id", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("user_message", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("code", sqlalchemy.Text),
    sqlalchemy.Column("stdout", sqlalchemy.Text),
    sqlalchemy.Column("traceback", sqlalchemy.Text),
)


class AuditLogger:
    """Persists a record of every chat interaction: which session asked what,
    what code ran against the data, and what it produced. This is the trail
    an org needs to satisfy compliance requirements around AI-assisted data
    access, since the sandbox itself is ephemeral and leaves nothing behind
    once a session closes."""

    def __init__(self, engine: sqlalchemy.Engine):
        self._engine = engine
        self._table_ready = False

    def _ensure_table(self) -> None:
        if not self._table_ready:
            metadata.create_all(self._engine, tables=[audit_log_table])
            self._table_ready = True

    def record(
        self,
        session_id: str,
        user_message: str,
        code: str | None,
        stdout: str | None,
        traceback: str | None,
    ) -> None:
        self._ensure_table()
        with self._engine.begin() as conn:
            conn.execute(
                audit_log_table.insert().values(
                    session_id=session_id,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    user_message=user_message,
                    code=code,
                    stdout=stdout,
                    traceback=traceback,
                )
            )
