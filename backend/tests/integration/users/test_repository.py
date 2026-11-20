from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Invite, Role
from atletico_hub.players.models import Player
from atletico_hub.users.repository import UserRepository


def add_account(db_session: DbSession, first_name: str, last_name: str, role: Role = Role.PLAYER) -> Account:
    account = Account(
        player=Player(first_name=first_name, last_name=last_name),
        email=f"{first_name}.{last_name}@example.com".lower(),
        password_hash="x",
        role=role,
        failed_logins=0,
    )
    db_session.add(account)
    db_session.flush()
    return account


class TestUserRepository:
    def test_list_accounts_sorts_by_last_name_then_first_name_and_skips_players_without_account(
        self, db_session: DbSession
    ) -> None:
        add_account(db_session, "Marco", "Rossi")
        add_account(db_session, "Anna", "Rossi")
        add_account(db_session, "Luca", "Bianchi")
        db_session.add(Player(first_name="Senza", last_name="Account"))
        db_session.flush()

        accounts = UserRepository(db_session).list_accounts()

        assert [(a.player.first_name, a.player.last_name) for a in accounts] == [
            ("Luca", "Bianchi"),
            ("Anna", "Rossi"),
            ("Marco", "Rossi"),
        ]

    def test_account_by_id_finds_an_account_and_answers_none_for_an_unknown_one(self, db_session: DbSession) -> None:
        account = add_account(db_session, "Anna", "Rossi")
        repository = UserRepository(db_session)

        assert repository.account_by_id(account.id) is account
        assert repository.account_by_id(0) is None

    def test_account_by_id_reads_the_row_again_instead_of_the_copy_in_the_session(self, db_session: DbSession) -> None:
        account = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        db_session.execute(
            update(Account)
            .where(Account.id == account.id)
            .values(role=Role.PLAYER)
            .execution_options(synchronize_session=False)
        )

        fresh = UserRepository(db_session).account_by_id(account.id)

        assert fresh is not None
        assert fresh.role == Role.PLAYER

    def test_lock_admins_answers_the_ids_of_the_admins_only(self, db_session: DbSession) -> None:
        admin = add_account(db_session, "Anna", "Rossi", Role.ADMIN)
        add_account(db_session, "Luca", "Bianchi")

        assert list(UserRepository(db_session).lock_admins()) == [admin.id]

    def test_delete_open_invites_of_player_keeps_used_invites_and_other_players(self, db_session: DbSession) -> None:
        anna = add_account(db_session, "Anna", "Rossi")
        luca = add_account(db_session, "Luca", "Bianchi")
        later = datetime.now(UTC) + timedelta(days=1)
        db_session.add_all(
            [
                Invite(player_id=anna.player_id, token_hash="open", expires_at=later),
                Invite(player_id=anna.player_id, token_hash="used", expires_at=later, used_at=datetime.now(UTC)),
                Invite(player_id=luca.player_id, token_hash="other", expires_at=later),
            ]
        )
        db_session.flush()

        UserRepository(db_session).delete_open_invites_of_player(anna.player_id)

        assert set(db_session.scalars(select(Invite.token_hash))) == {"used", "other"}
