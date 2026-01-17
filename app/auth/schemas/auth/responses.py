from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., description="New access token")


class OAuthUrlResponse(BaseModel):
    url: str