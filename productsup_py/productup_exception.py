# Author: Lyes Tarzalt
class ProductsUpError(Exception):
    def __init__(self, status_code=None, message=None, site_id=None, project_id=None):
        self.status_code = status_code
        self.message = message
        self.site_id = site_id

    def __str__(self):
        return f"Code:{self.status_code} {self.message}"


class SiteNotFoundError(ProductsUpError):
    """The specified entity could not be found"""

    def __str__(self):
        return f"Site not found: {self.site_id}"


class ProjectNotFoundError(ProductsUpError):
    """The specified entity could not be found"""

    def __str__(self):
        return f"Project not found: {self.project_id}"


class ProjectAlreadyExistsError(ProductsUpError):
    pass


class SiteAlreadyExistsError(ProductsUpError):
    pass


class EmptySiteError(ProductsUpError):
    """The Site has no information"""
    pass


class BadRequestError(ProductsUpError):
    """Your request was malformed"""

    def __str__(self):
        return f"Code: {self.status_code} {self.message}"


class UnauthorizedError(ProductsUpError):
    """Invalid authentication token used"""

    def __str__(self):
        return f"Code:{self.status_code} Unauthorized. Wrong credentials"


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
