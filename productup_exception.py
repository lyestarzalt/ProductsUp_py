class ProductsUpError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"{self.status_code}: {self.message}"


class BadRequestError(ProductsUpError):
    """Your request was malformed"""
    pass


class UnauthorizedError(ProductsUpError):
    """Invalid authentication token used"""
    pass


class ForbiddenError(ProductsUpError):
    """The entity requested is hidden for administrators only"""
    pass


class NotFoundError(ProductsUpError):
    """The specified entity could not be found"""
    pass


class MethodNotAllowedError(ProductsUpError):
    """You tried to access a entity with an invalid method"""
    pass


class NotAcceptableError(ProductsUpError):
    """You requested a format that isn't json"""
    pass


class GoneError(ProductsUpError):
    """The entity requested has been removed from our servers"""
    pass


class InternalServerError(ProductsUpError):
    """Temporarily offline for maintenance"""
    pass
