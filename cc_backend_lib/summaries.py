
import asyncio
from typing import Optional, TypeVar
from toolz.functoolz import curry

from pymonad.either import Right, Either

from cc_backend_lib.clients import predictions_client, scheduler_client, users_client, countries_client
from cc_backend_lib.cache import dummy_cache, cache
from cc_backend_lib.errors import http_error
from cc_backend_lib import models, async_either, helpers

T = TypeVar("T")
U = TypeVar("U")

class Summaries():
    """
    Summaries
    =========

    parameters:
        predictions (cc_backend_lib.clients.predictions_client.PredictionsClient)
        scheduler   (cc_backend_lib.clients.scheduler_client.SchedulerClient)
        users       (cc_backend_lib.clients.users_client.UsersClient)
        countries   (cc_backend_lib.clients.countries_client.CountriesClient)
        cache_class (cc_backend_lib.cache.Cache)

    A class that can be used to fetch various useful summaries.
    """
    def __init__(self,
            predictions: predictions_client.PredictionsClient,
            scheduler: scheduler_client.SchedulerClient,
            users: users_client.UsersClient,
            countries: countries_client.CountriesClient,
            cache_class: cache.Cache = dummy_cache.DummyCache()):

        self._predictions = predictions
        self._scheduler = scheduler
        self._users = users
        self._cache = cache_class
        self._countries = countries

    async def participants(self,
            shift: int = 0,
            country_id: Optional[int] = None
            ) -> Either[http_error.HttpError, models.emailer.ParticipationSummary]:
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

        schedule = await self._scheduler.time_partition(shift)

        kwargs = async_either.AsyncEither.from_either((schedule
            .then(lambda time_partition: {"start_date": time_partition.start, "end_date": time_partition.end})
            .then(lambda kwargs: helpers.dictadd(kwargs, {"country":country_id}) if country_id is not None else kwargs)))

        predictions = await kwargs.async_map(curry(helpers.expand_kwargs, self._predictions.list))
        predictions = predictions.to_either()

        author_ids = async_either.AsyncEither.from_either(
                predictions.then(lambda preds: {p.properties["author"] for p in preds.features}))

        authors = (author_ids
                    .then(lambda ids: [self._users.detail(id) for id in ids]))

        authors = await authors.async_map(curry(helpers.expand_args,asyncio.gather))
        authors = (authors
                .then(helpers.combine_http_errors)
                .then(lambda a: models.user.UserList(users = a)))

        if country_id:
            country = await self._countries.detail(country_id)
        else:
            country = Right(None)

        return Either.apply(curry(lambda a, c, s: models.emailer.ParticipationSummary.from_user_list(
                user_list = a,
                partition = s,
                country_feature = c
            ))).to_arguments(authors, country, schedule)
