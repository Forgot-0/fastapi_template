# from datetime import datetime, timedelta
# from uuid import uuid4
# from jose import jwt, JWTError
 

# def create_refresh_token(day) -> str:
#     """
#     Create a refresh token with an optional expiration time.

#     :param data: The data to encode in the token.
#     :param expires_delta: Optional timedelta for token expiration.
#     :return: The encoded JWT refresh token.
#     """
#     ttl = timedelta(days=day)
#     expire = ttl.total_seconds()

#     to_encode = {
#         "type": "refresh",
#         "exp": expire
#     }

#     encoded_jwt = jwt.encode(to_encode, "qeqw", algorithm='HS256')
#     return encoded_jwt



# print(create_refresh_token(day=2))
# print(create_refresh_token(day=3))
