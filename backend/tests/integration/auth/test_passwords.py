from atletico_hub.auth.passwords import Argon2PasswordHasher


class TestArgon2PasswordHasher:
    def test_verify_accepts_its_own_hash(self) -> None:
        hasher = Argon2PasswordHasher()
        password_hash = hasher.hash(password="calcetto del martedi")

        assert password_hash != "calcetto del martedi"
        assert hasher.verify(password="calcetto del martedi", password_hash=password_hash) is True

    def test_verify_rejects_another_password(self) -> None:
        hasher = Argon2PasswordHasher()
        password_hash = hasher.hash(password="calcetto del martedi")

        assert hasher.verify(password="calcetto del giovedi", password_hash=password_hash) is False
