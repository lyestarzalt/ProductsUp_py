# Author: Lyes Tarzalt

import requests
from productup_exception import BadRequestError, UnauthorizedError, ForbiddenError, \
    NotFoundError, MethodNotAllowedError,\
    NotAcceptableError, GoneError, InternalServerError, ProductsUpError


class ProductUpAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
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

    def make_request(self, url: str, method: str = None, data: dict = None) -> dict:
        token = self.get_token()
        if method == "get":
            response = self.session.get(url=url, headers=token)
        elif method == "post":
            response = self.session.post(url=url, headers=token, data=data)
        elif method == "put":
            response = self.session.put(url=url, headers=token, data=data)
        elif method == "delete":
            response = self.session.delete(url=url, headers=token, data=data)

        if response.status_code not in range(200, 299):
            exception_class = self.status_code_exceptions.get(
                response.status_code, None)
            if exception_class:
                raise exception_class(
                    response.status_code, response.json().get("message"))
            else:
                raise ProductsUpError(
                    response.status_code, response.json().get("message"))
        return response.json()


if __name__ == '__main__':

    pass
