
from typing import Optional
import datetime
import json
import base64
from pymonad.either import Left, Right, Either
from cc_backend_lib.errors import http_error
from cc_backend_lib import models
from . import model_api_client

class UsersClient(model_api_client.ModelApiClient[models.user.UserDetail, models.user.UserList]):
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

    def deserialize_detail(self, data:bytes)-> Either[http_error.HttpError, models.user.UserDetail]:
        try:
            data = models.user.UserDetail(**json.loads(data))
            if self._anonymize:
                data.scrub()
            return Right(data)
        except Exception:
            return Left(http_error.HttpError(message= f"Failed to deserialize: {data}", http_code = 500))

    def deserialize_list(self, data:bytes)-> Either[http_error.HttpError, models.user.UserList]:
        try:
            data = models.user.UserList(**json.loads(data))
            if self._anonymize:
                data.scrub()
            return Right(data)
        except Exception as e:
            return Left(http_error.HttpError(message = str(e), http_code = 500))

    async def set_email_subscription_status(self, name: str, status: bool) -> Either[http_error.HttpError, models.user.UserEmailStatus]:
        """
        set_email_subscription_status
        =============================

        parameters:
            name (str): Name (user id) of the user to set cooldown status for
            status (bool)
        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.user.UserEmailStatus]
        """

        parameters = self._parameters({})
        result = await self._request("put",
                self._path(name) + "/email-subscription",
                parameters = parameters,
                json = models.user.EmailStatus(has_unsubscribed = status).dict())
        return result.then(lambda data: models.user.UserEmailStatus(**json.loads(data)))

    async def id_from_email(self, email: str) -> Either[http_error.HttpError, models.user.UserDetail]:
        """
        id_from_email
        =============

        parameters:
            email (str)
        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.user.UserDetail]

        Get a user profile based on their email.
        """

        encoded_email = base64.b16encode(email.encode()).decode()

        result = await self._request("get",
                self._path("") + f"whois-email/{encoded_email}",
                parameters = self._parameters({}))

        return result.then(lambda data: models.user.UserIdentification(**json.loads(data)))

    async def set_email_cooldown_status(self, name: str, last_mailed: Optional[datetime.date] = None):
        """
        set_email_cooldown_status
        =========================

        parameters:
            name (str): Name (user id) of the user to set cooldown status for
            last_mailed (Optional[datetime.date]): If None, datetime.date.today() is used
        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.user.EmailCooldownStatus]
        """

        if last_mailed is None:
            last_mailed = datetime.date.today()

        result = await self._request("put",
                self._path(name) + "/last-emailed",
                parameters = self._parameters({}),
                data = models.user.EmailCooldownStatus(last_mailed = last_mailed).json().encode(),
                headers = {"content-type":"application/json"})

        return result.then(lambda data: models.user.EmailCooldownStatus(**json.loads(data)))
