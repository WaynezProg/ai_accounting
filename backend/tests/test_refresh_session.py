import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.config import settings
from app.database.engine import Base
from app.database.crud import create_user, save_refresh_token, get_refresh_token_by_user
from app.services.jwt_service import jwt_service
from app.api.auth import refresh_session, RefreshTokenRequest


class RefreshSessionTests(unittest.TestCase):
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

    def _issue_refresh_token(self) -> str:
        refresh_token = jwt_service.create_refresh_token()
        refresh_hash = jwt_service.hash_refresh_token(refresh_token)
        save_refresh_token(self.db, user_id=self.user.id, token_hash=refresh_hash)
        return refresh_token

    def test_refresh_rotation_invalidates_old_token(self):
        refresh_token = self._issue_refresh_token()

        response = refresh_session(
            RefreshTokenRequest(refresh_token=refresh_token),
            db=self.db,
        )
        self.assertTrue(response.access_token)
        self.assertNotEqual(response.refresh_token, refresh_token)

        with self.assertRaises(HTTPException) as context:
            refresh_session(
                RefreshTokenRequest(refresh_token=refresh_token),
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, 401)

    def test_inactivity_logout(self):
        refresh_token = self._issue_refresh_token()
        token_record = get_refresh_token_by_user(self.db, self.user.id)
        # 使用設定值 + 1 小時，確保超過 inactivity threshold
        inactivity_hours = settings.JWT_REFRESH_INACTIVITY_HOURS + 1
        token_record.last_used_at = datetime.utcnow() - timedelta(
            hours=inactivity_hours
        )
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            refresh_session(
                RefreshTokenRequest(refresh_token=refresh_token),
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, 401)

    def test_single_device_invalidation(self):
        first_refresh = self._issue_refresh_token()
        _ = self._issue_refresh_token()

        with self.assertRaises(HTTPException) as context:
            refresh_session(
                RefreshTokenRequest(refresh_token=first_refresh),
                db=self.db,
            )
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
