from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DbSession

from atletico_hub.auth.models import Account, Invite, Session
from atletico_hub.players.models import Player


class AuthRepository:
    def __init__(self, session: DbSession) -> None:
        self._session = session

    def player_by_id(self, player_id: int) -> Player | None:
        return self._session.get(Player, player_id)

    def add_account(self, account: Account) -> Account:
        self._session.add(account)
        self._session.flush()
        return account

    def account_by_email(self, email: str) -> Account | None:
        return self._session.scalar(select(Account).where(Account.email == email))

    def account_by_player(self, player_id: int) -> Account | None:
        return self._session.scalar(select(Account).where(Account.player_id == player_id))

    def add_session(self, session: Session) -> Session:
        self._session.add(session)
        self._session.flush()
        return session

    def session_by_token_hash(self, token_hash: str) -> Session | None:
        return self._session.scalar(select(Session).where(Session.token_hash == token_hash))

    def delete_session(self, session: Session) -> None:
        self._session.delete(session)
        self._session.flush()

    def delete_sessions_of_account(self, account_id: int) -> None:
        self._session.execute(delete(Session).where(Session.account_id == account_id))

    def add_invite(self, invite: Invite) -> Invite:
        self._session.add(invite)
        self._session.flush()
        return invite

    def invite_by_token_hash(self, token_hash: str) -> Invite | None:
        return self._session.scalar(select(Invite).where(Invite.token_hash == token_hash))

    def delete_open_invites_of_player(self, player_id: int) -> None:
        self._session.execute(delete(Invite).where(Invite.player_id == player_id, Invite.used_at.is_(None)))
