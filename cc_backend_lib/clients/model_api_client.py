
import abc
from typing import Generic, TypeVar
from pymonad.either import Either
from cc_backend_lib.errors import http_error
from . import api_client

T = TypeVar("T")
U = TypeVar("U")

class ModelApiClient(api_client.ApiClient, abc.ABC, Generic[T,U]):
    """
    ApiClient
    =========

    Generic client for interacting with a RESTful API that yields pydantic
    de-serializable JSON data. To use this class, subclass and:
        * override deserialize method
        * T type for detail model
        * U type for list model
    """

    @abc.abstractmethod
    def deserialize_detail(self, data: bytes)-> Either[http_error.HttpError, T]:
        pass

    @abc.abstractmethod
    def deserialize_list(self, data: bytes)-> Either[http_error.HttpError, U]:
        pass

    async def detail(self, name: str, **kwargs) -> Either[http_error.HttpError, T]:
        """
        detail
        ======

        parameters:
            name (str)
        returns:
            Either[cc_backend_client.http_error.HttpError, T]

        Get and deserialize a resource named name
        """
        name = str(name).strip("/") + "/"

        path = self._path(name)
        parameters = {str(k): str(v) for k,v in kwargs.items()}
        response = await self._get(path, parameters = self._parameters(parameters))
        return response.then(self.deserialize_detail)

    async def list(self, page: int = 0, **kwargs) -> Either[http_error.HttpError, U]:
        """
        list
        ====
        parameters:
            **kwargs: Passed as query parameters to request

        returns:
            Either[cc_backend_client.http_error.HttpError, U]

        Show a list of available resources (optional pageination).
        """
        parameters = self._parameters({"page": str(page)} if page else {})
        parameters.update({str(k): str(v) for k,v in kwargs.items()})
        path = self._path("")
        response = await self._get(path, parameters = parameters)
        return response.then(self.deserialize_list)
