from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from interface import dependencies, schemas
from interface.api.v1.endpoints.auth import login_for_access_token as auth_login

router = APIRouter()


@router.post(
    "/access-token", response_model=schemas.Token, summary="Obtain Access Token"
)
def login_access_token(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate user and return access token.
    """
    return auth_login(db, form_data)
