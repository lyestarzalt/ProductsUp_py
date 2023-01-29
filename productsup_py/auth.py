# Author: Lyes Tarzalt
# ProductsUpPy is a Python wrapper for the ProductsUp API.
import aiohttp

import requests
from productsup_py.errors.productup_exception import BadRequestError, UnauthorizedError, ForbiddenError, \
    NotFoundError, MethodNotAllowedError,\
    NotAcceptableError, GoneError, InternalServerError


class ProductUpAuth:
    def __init__(self, client_id, client_secret):
        self.token = f"{client_id}:{client_secret}"

        self.session = requests.Session()

        self.status_code_exceptions = {
            400: BadRequestError,
            401: UnauthorizedError,
            403: ForbiddenError,
            404: NotFoundError,
            405: MethodNotAllowedError,
            406: NotAcceptableError,
            410: GoneError,
            500: InternalServerError
        }

    def get_token(self) -> dict:
        return {"X-Auth-Token": self.token}

    def make_request(self, url: str, method: str, data: dict = {}) -> requests.Response:
        token = self.get_token()
        if method == "get":
            response = self.session.get(url=url, headers=token)
        elif method == "post":
            response = self.session.post(url=url, headers=token, data=data)
        elif method == "put":
            response = self.session.put(url=url, headers=token, data=data)
        elif method == "delete":
            response = self.session.delete(url=url, headers=token, data=data)
        else:
            raise ValueError("Method not allowed")
        response_body = response.json()
        if response.status_code in self.status_code_exceptions:
            raise self.status_code_exceptions[response.status_code](
                response.status_code, response_body["message"])
        else:
            return response
