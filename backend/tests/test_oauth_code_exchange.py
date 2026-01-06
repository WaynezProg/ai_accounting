import unittest
from datetime import datetime, timedelta
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.database.engine import Base
from app.database.crud import create_user, create_oauth_login_code
from app.api.auth import exchange_oauth_code, ExchangeCodeRequest


class OAuthCodeExchangeTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite:///:memory:", connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine)
        self.db = self.SessionLocal()

        self.user = create_user(
            self.db,
            user_id="test-user",
            email="test@example.com",
            name="Test User",
        )

    def tearDown(self):
        self.db.close()

    def _issue_code(self, raw_code: str, expires_minutes: int = 5) -> str:
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        create_oauth_login_code(
            self.db,
            user_id=self.user.id,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        return raw_code

    def test_exchange_success_and_single_use(self):
        raw_code = self._issue_code("sample-code")

        response = exchange_oauth_code(
            ExchangeCodeRequest(code=raw_code),
            db=self.db,
        )
        self.assertTrue(response.access_token)
        self.assertTrue(response.refresh_token)

        with self.assertRaises(HTTPException) as context:
            exchange_oauth_code(
                ExchangeCodeRequest(code=raw_code),
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, 401)

    def test_exchange_expired_code(self):
        raw_code = self._issue_code("expired-code", expires_minutes=-1)

        with self.assertRaises(HTTPException) as context:
            exchange_oauth_code(
                ExchangeCodeRequest(code=raw_code),
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
