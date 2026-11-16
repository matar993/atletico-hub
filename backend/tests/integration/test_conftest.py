from sqlalchemy import Engine, text
from sqlalchemy.orm import Session


class TestDbSession:
    def test_commit_stays_inside_the_test_transaction(self, db_engine: Engine, db_session: Session) -> None:
        db_session.execute(text("CREATE TABLE probe (id integer)"))
        db_session.execute(text("INSERT INTO probe (id) VALUES (1)"))
        db_session.commit()

        assert db_session.execute(text("SELECT id FROM probe")).scalar_one() == 1
        with db_engine.connect() as other:
            assert other.execute(text("SELECT to_regclass('probe')")).scalar_one() is None
