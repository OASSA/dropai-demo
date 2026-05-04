from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Request
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.audit import log_action


class AuthService:
    async def login(self, db: AsyncSession, payload: LoginRequest, request: Request = None) -> TokenResponse:
        repo = UserRepository(db)
        user = await repo.get_by_email(payload.email)

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        token_data = {"sub": str(user.id), "role": user.role.name, "company": user.company_id}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        ip = request.client.host if request else None
        ua = request.headers.get("user-agent") if request else None
        await log_action(
            db,
            action="LOGIN",
            resource_type="user",
            resource_id=str(user.id),
            user_id=user.id,
            description=f"User {user.email} logged in",
            ip_address=ip,
            user_agent=ua,
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, db: AsyncSession, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        repo = UserRepository(db)
        user = await repo.get(int(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        token_data = {"sub": str(user.id), "role": user.role.name, "company": user.company_id}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )


auth_service = AuthService()
