import sqlalchemy

from charissa.audit import AuditLogger
from charissa.audit.logger import audit_log_table


def _in_memory_logger() -> AuditLogger:
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    return AuditLogger(engine), engine


def test_record_persists_interaction():
    logger, engine = _in_memory_logger()

    logger.record(
        session_id="abc123",
        user_message="hitung 2+2",
        code="print(2+2)",
        stdout="4\n",
        traceback="",
    )

    with engine.connect() as conn:
        rows = conn.execute(sqlalchemy.select(audit_log_table)).fetchall()

    assert len(rows) == 1
    assert rows[0].session_id == "abc123"
    assert rows[0].user_message == "hitung 2+2"
    assert rows[0].stdout == "4\n"


def test_record_multiple_interactions_same_session():
    logger, engine = _in_memory_logger()

    logger.record(session_id="s1", user_message="first", code=None, stdout=None, traceback=None)
    logger.record(session_id="s1", user_message="second", code=None, stdout=None, traceback=None)

    with engine.connect() as conn:
        rows = conn.execute(sqlalchemy.select(audit_log_table)).fetchall()

    assert len(rows) == 2
    assert [r.user_message for r in rows] == ["first", "second"]
