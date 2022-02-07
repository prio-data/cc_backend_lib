
import asyncio
from typing import Optional, List, TypeVar
from functools import reduce

from pymonad.maybe import Maybe, Just, Nothing
from pymonad.either import Left, Right, Either

from cc_backend_lib.clients import predictions_client, scheduler_client, users_client
from cc_backend_lib.cache import dummy_cache, cache
from cc_backend_lib.errors import http_error
from cc_backend_lib import models

T = TypeVar("T")

class Summaries():
    def __init__(self,
            predictions: predictions_client.PredictionsClient,
            scheduler: scheduler_client.SchedulerClient,
            users: users_client.UsersClient,
            cache_class: cache.Cache = dummy_cache.DummyCache()):

        self._predictions = predictions
        self._scheduler = scheduler
        self._users = users
        self._cache = cache_class

    async def participants(self, shift: int = 0, country_id: Optional[int] = None) -> Either[http_error.HttpError, models.user.UserList]:
        """
        participants
        ============

        parameters:
            shift (int) = 0
            country_id (Optional[int]) = None

        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.user.UserList]

        Fetches a userlist corresponding to users that participated (added
        predictions) for a given country.
        """
        # Check cache first, before making all of the requests...

        schedule = await self._scheduler.time_partition(shift)

        kwargs = (schedule
            .then(lambda time_partition: {"start_date": time_partition.start, "end_date": time_partition.end})
            .then(lambda kwargs: _dictadd(kwargs, {"country":country_id}) if country_id is not None else kwargs))

        if kwargs.is_right():
            predictions = await self._predictions.list(**kwargs.value)
            author_ids = predictions.then(lambda preds: {p.properties["author"] for p in preds.features})
            if author_ids.is_right():
                authors = await asyncio.gather(*[self._users.detail(str(i)) for i in author_ids.value])
                authors = _sequence(map(lambda a: a.either(lambda _: Nothing, Just),authors))

                return authors.maybe(
                        Left(http_error.HttpError(http_code =500)),
                        lambda authors: Right(models.user.UserList(users= authors)))
            else:
                return author_ids
        else:
            return kwargs

def _dictadd(a,b):
    return dict(list(a.items()) + list(b.items()))

def _sequence(maybes: List[Maybe[T]]) -> Maybe[List[T]]:
    return reduce(lambda a,b: a.then(lambda x: b.then(lambda y: x + [y])), maybes, Just([]))
