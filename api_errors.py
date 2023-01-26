class ApiError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"{self.status_code}: {self.message}"


class BadRequestError(ApiError):
    """Your request was malformed"""
    pass

class UnauthorizedError(ApiError):
    """Invalid authentication token used"""
    pass

class ForbiddenError(ApiError):
    """The entity requested is hidden for administrators only"""
    pass

class NotFoundError(ApiError):
    """The specified entity could not be found"""
    pass

class MethodNotAllowedError(ApiError):
    """You tried to access a entity with an invalid method"""
    pass

class NotAcceptableError(ApiError):
    """You requested a format that isn't json"""
    pass

class GoneError(ApiError):
    """The entity requested has been removed from our servers"""
    pass

class InternalServerError(ApiError):
    """Temporarily offline for maintenance"""
    pass
