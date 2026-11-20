from atletico_hub.auth.tokens import generate_token, hash_token


class TestTokens:
    def test_generate_token_gives_a_different_url_safe_token_each_time(self) -> None:
        first = generate_token()
        second = generate_token()

        assert first != second
        assert len(first) >= 43
        assert first.replace("-", "").replace("_", "").isalnum()

    def test_hash_token_is_the_sha256_hex_digest(self) -> None:
        assert hash_token(token="abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

    def test_hash_token_is_stable_and_differs_between_tokens(self) -> None:
        assert hash_token(token="one") == hash_token(token="one")
        assert hash_token(token="one") != hash_token(token="two")
