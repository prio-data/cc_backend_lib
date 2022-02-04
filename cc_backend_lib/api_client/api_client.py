import logging
import os
import abc
from typing import Dict, Optional
import aiohttp
from pymonad.either import Either, Left, Right
from cc_backend_lib.errors import http_error

logger = logging.getLogger(__name__)

class ApiClient(abc.ABC):
    """
    ApiClient
    =========
    """
    def __init__(self, base_url: str, path: str = "", base_parameters: Optional[Dict[str,str]] = None):
        self._base_url                = base_url
        self._api_path                = path
        self._headers: Dict[str, str] = {}
        self._cookies: Dict[str, str] = {}
        self._base_parameters         = {} if base_parameters is None else base_parameters

    def _parameters(self, parameters: Optional[Dict[str,str]] = None):
        base = self._base_parameters.copy()
        base.update(parameters if parameters is not None else {})
        return base

    async def _get(self, path: str, parameters: Dict[str,str]) -> Either[http_error.HttpError, bytes]:
        async with self._session() as session:
            async with session.get(path, params = parameters) as response:
                logger.debug(f"Requested {response.url} ({response.status})")
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
