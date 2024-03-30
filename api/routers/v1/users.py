import re
from fastapi import APIRouter, HTTPException, status, Depends
from api.schemas import types
from api.deps import get_db
from sqlalchemy.orm import Session
from api.services import auth
from api.helpers import http

router = APIRouter()


@router.post('/login')
async def login(user_credentials: types.UserLogin, db: Session = Depends(get_db)):
    user = user_credentials.model_dump()
    results = []
    if user['email'] == '' or user['password'] == '':
        return {
            'message': 'Dear user, credentials empty.',
            status: status.HTTP_204_NO_CONTENT,
        }

    token = auth.access(user=user, db=db)

    results.append({'access_token': token, 'token_type': 'Bearer'})

    return http.response(
        message='User logger successfuly', db=results, status=status.HTTP_200_OK
    )


@router.post('/register')
async def register(user_credentials: types.UserCreate, db: Session = Depends(get_db)):
    user = user_credentials.model_dump()

    if len(user['password']) <= 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='The password must be more than 7 characters',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    patternMayus = re.compile(r'[A-Z]')

    if not patternMayus.search(user['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='Password must have at least one uppercase letter',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    patternCharacter = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]')

    if not patternCharacter.search(user['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='Password must have at least one character special',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    if user['role'] not in ['admin', 'user']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='The selected role is incorrect',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    pattern = re.compile(r'[^@]+@[^@]+\.[^@]+')

    if not pattern.match(user['email']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='This email is not valid',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    if not user['name'] or len(user['name']) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='The name is not valid',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    if not user['phone'].isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=http.response(
                message='The number is not valid',
                status=status.HTTP_400_BAD_REQUEST,
            ),
        )

    auth.create(user=user, db=db)

    return http.response(message='The number is not valid')
