
import json
from pymonad.either import Left, Right, Either
from cc_backend_lib.errors import http_error
from cc_backend_lib import models
from . import model_api_client

class UsersClient(model_api_client.ModelApiClient[models.user.User, models.user.UserList]):
    """
    UsersClient
    ===========

    parameters:
        base_url (str):   URL poiting to API exposing users
        path (str):       Path in API that exposes users = ""
        anonymize (bool): Anonymize user data on retrieval = False

    A client that is used to fetch user data from an API.
    """

    def __init__(self, base_url: str, path: str = "", anonymize: bool = False):
        super().__init__(base_url, path)
        self._anonymize = anonymize

    def deserialize_detail(self, data:bytes)-> Either[http_error.HttpError, models.user.User]:
        try:
            data = models.user.User(**json.loads(data))
            if self._anonymize:
                data.scrub()
            return Right(data)
        except Exception:
            return Left(http_error.HttpError(message= f"Failed to deserialize: {data}", http_code = 500))

    def deserialize_list(self, data:bytes)-> Either[http_error.HttpError, models.user.UserList]:
        try:
            data = models.user.UserList(users = json.loads(data))
            if self._anonymize:
                data.scrub()
            return Right(data)
        except Exception as e:
            return Left(http_error.HttpError(message = str(e), http_code = 500))
