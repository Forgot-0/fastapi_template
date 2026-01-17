import pytest

from app.auth.services.hash import HashService


@pytest.mark.unit
@pytest.mark.auth
class TestHashService:

    def test_hash_password_basic(self, hash_service: HashService):
        password = "TestPassword123!"
        hashed = hash_service.hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2")

    def test_same_password_different_hashes(self, hash_service: HashService):
        password = "TestPassword123!"
        hash1 = hash_service.hash_password(password)
        hash2 = hash_service.hash_password(password)

        assert hash1 != hash2

    def test_verify_correct_and_incorrect(self, hash_service: HashService):
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True
        assert hash_service.verify_password(wrong_password, hashed) is False
        assert hash_service.verify_password("", hashed) is False

    def test_hash_empty_password(self, hash_service: HashService):
        hashed = hash_service.hash_password("")
        assert hashed is not None
        assert hash_service.verify_password("", hashed) is True

    @pytest.mark.parametrize("password", [
        "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "Пароль123!中文密码",
        "A" * 200,
    ])
    def test_special_unicode_long_passwords(self, hash_service: HashService, password: str):
        hashed = hash_service.hash_password(password)
        assert hash_service.verify_password(password, hashed) is True

    def test_verify_case_and_whitespace_sensitive(self, hash_service: HashService):
        password = "Test Password"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password("TestPassword", hashed) is False
        assert hash_service.verify_password(" Test Password", hashed) is False
        assert hash_service.verify_password("Test Password ", hashed) is False

        pass_case = "TestPassword"
        hashed_case = hash_service.hash_password(pass_case)
        assert hash_service.verify_password("testpassword", hashed_case) is False
        assert hash_service.verify_password("TESTPASSWORD", hashed_case) is False
        assert hash_service.verify_password(pass_case, hashed_case) is True

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
