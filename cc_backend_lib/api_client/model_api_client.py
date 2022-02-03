
import os
import abc
from typing import Generic, TypeVar, Dict, Optional
import aiohttp
from pymonad.either import Either, Left, Right
from cc_backend_lib.errors import http_error

T = TypeVar("T")
U = TypeVar("U")

class ModelApiClient(abc.ABC, Generic[T,U]):
    """
    ApiClient
    =========

    Generic client for interacting with a RESTful API that yields pydantic
    de-serializable JSON data. To use this class, subclass and:
        * override deserialize method
        * T type for detail model
        * U type for list model
    """
    def __init__(self, base_url: str, path: str = "", base_parameters: Optional[Dict[str,str]] = None):
        self._base_url                = base_url
        self._api_path                = path
        self._headers: Dict[str, str] = {}
        self._cookies: Dict[str, str] = {}
        self._base_parameters         = {} if base_parameters is None else base_parameters

    @abc.abstractmethod
    def deserialize_detail(self, data: bytes)-> Either[http_error.HttpError, T]:
        pass

    @abc.abstractmethod
    def deserialize_list(self, data: bytes)-> Either[http_error.HttpError, U]:
        pass

    def _parameters(self, parameters: Optional[Dict[str,str]] = None):
        base = self._base_parameters.copy()
        base.update(parameters if parameters is not None else {})
        return base

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
        name = name.strip("/") + "/"

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

    async def _get(self, path: str, parameters: Dict[str,str]) -> Either[http_error.HttpError, bytes]:
        async with self._session() as session:
            async with session.get(path, params = parameters) as response:
                content = await response.read()

                if self._status_is_ok(response.status):
                    return Right(content)
                else:
                    return Left(http_error.HttpError(
                            url = self._base_url + path,
                            http_code = response.status,
                            content = content
                            ))

    def _path(self, name: str) -> str:
        return "/"+os.path.join(self._api_path,name)

    def _status_is_ok(self, status: int) -> bool:
        return status == 200

    def _session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
                base_url = self._base_url,
                headers = self._headers,
                cookies = self._cookies)
