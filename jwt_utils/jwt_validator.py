# -*- coding: utf-8 -*-
"""
class used for jwt validator
"""
import jwt
from rest_framework import exceptions

from jwt_utils.encryption import AESCipher
from invoice_gen import settings
from invoice_gen.settings import JWT_ALGORITHM

jwt_secret = settings.JWT_SECRET
options = {"verify_exp": True}


def jwt_validator(token):
    try:
        obj = AESCipher()
        decoded = obj.decrypt_token(token)
        payload = jwt.decode(
            decoded, jwt_secret, algorithm=JWT_ALGORITHM, options=options
        )
        return payload
    except Exception:
        raise exceptions.AuthenticationFailed
