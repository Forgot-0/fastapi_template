import pytest

from app.auth.services.hash import HashService


@pytest.mark.unit
@pytest.mark.auth
class TestHashService:

    def test_hash_password(self, hash_service: HashService):
        password = "TestPassword123!"

        hashed = hash_service.hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")

    def test_same_password_different_hashes(self, hash_service: HashService):
        password = "TestPassword123!"

        hash1 = hash_service.hash_password(password)
        hash2 = hash_service.hash_password(password)

        assert hash1 != hash2

    def test_verify_correct_password(self, hash_service: HashService):
        password = "TestPassword123!"
        hashed = hash_service.hash_password(password)

        result = hash_service.verify_password(password, hashed)

        assert result is True

    def test_verify_incorrect_password(self, hash_service: HashService):
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_service.hash_password(password)

        result = hash_service.verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_empty_password(self, hash_service: HashService):
        password = "TestPassword123!"
        hashed = hash_service.hash_password(password)

        result = hash_service.verify_password("", hashed)

        assert result is False

    def test_hash_empty_password(self, hash_service: HashService):
        hashed = hash_service.hash_password("")

        assert hashed is not None
        assert hash_service.verify_password("", hashed) is True

    def test_hash_special_characters(self, hash_service: HashService):
        password = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True

    def test_hash_unicode_password(self, hash_service: HashService):
        password = "Пароль123!中文密码"

        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True

    def test_hash_long_password(self, hash_service: HashService):
        password = "A" * 200

        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True

    def test_verify_case_sensitive(self, hash_service: HashService):
        password = "TestPassword"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password("testpassword", hashed) is False
        assert hash_service.verify_password("TESTPASSWORD", hashed) is False
        assert hash_service.verify_password(password, hashed) is True

    def test_verify_whitespace_sensitive(self, hash_service: HashService):
        password = "Test Password"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password("TestPassword", hashed) is False
        assert hash_service.verify_password(" Test Password", hashed) is False
        assert hash_service.verify_password("Test Password ", hashed) is False

    def test_hash_consistency(self, hash_service: HashService):
        password = "TestPassword123!"
        hashed = hash_service.hash_password(password)

        for _ in range(10):
            assert hash_service.verify_password(password, hashed) is True

    @pytest.mark.parametrize("password", [
        "simple",
        "Complex123!",
        "very_long_password_with_many_characters_123456789",
        "12345678",
        "!@#$%^&*()",
        "Пароль",
    ])
    def test_various_passwords(self, hash_service: HashService, password: str):
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True
        assert hash_service.verify_password(password + "x", hashed) is False