
import asyncio
from typing import Optional, TypeVar
from toolz.functoolz import curry

from pymonad.either import Either

from cc_backend_lib.clients import predictions_client, scheduler_client, users_client, countries_client
from cc_backend_lib.cache import dummy_cache, cache
from cc_backend_lib.errors import http_error
from cc_backend_lib import models, async_either, helpers

T = TypeVar("T")
U = TypeVar("U")

class Dal():
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

    async def predictions(self, shift: int, country_id: int) -> Either[http_error.HttpError, models.prediction.PredFeatureCollection]:
        """
        predictions
        ===========

        parameters:
            shift (int)
            country_id (int)

        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.prediction.PredFeatureCollection]

        Returns a FeatureCollection of prediction features filtered in time via
        the scheduler (+shift) and in space via the country_id.
        """
        schedule = await self.time_partition(shift)
        return await async_either.AsyncEither.from_either(schedule).async_then(curry(self._predictions_in_partition, country_id))

    async def time_partition(self, shift: int) -> Either[http_error.HttpError, models.time_partition.TimePartition]:
        """
        time_partition
        ==============

        parameters:
            shift (int)

        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.time_partition.TimePartition]
        """
        return await self._scheduler.time_partition(shift)

    async def participants(self, shift: int = 0 , country_id: Optional[int] = None) -> Either[http_error.HttpError, models.user.UserList]:
        """
        participants
        ============

        parameters:
            shift (int)
            country_id (int)

        returns:
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.user.UserList]

        Returns a UserList of participants for a given shift / country_id
        combination.
        """
        predictions = await self.predictions(shift, country_id)
        users = await async_either.AsyncEither.from_either(predictions).async_then(self._prediction_authors)
        return users

    async def participant_summary(self,
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
            Either[cc_backend_lib.errors.http_error.HttpError, cc_backend_lib.models.emailer.ParticipationSummary]

        Returns a summary of participation for a time (shift) and country
        (country_id, optional).
        """

        schedule = await self.time_partition(shift)
        schedule = async_either.AsyncEither.from_either(schedule)

        predictions = await schedule.async_then(curry(self._predictions_in_partition, country_id))
        predictions = async_either.AsyncEither.from_either(predictions)

        authors = await predictions.async_then(self._prediction_authors)
        countries = await predictions.async_then(self._prediction_countries)

        return Either.apply(curry(lambda a, c, s: models.emailer.ParticipationSummary.from_user_list(
                user_list = a,
                partition = s,
                countries = c
            ))).to_arguments(authors, countries, schedule)

    async def _prediction_authors(self, predictions: models.prediction.PredFeatureCollection) -> Either[http_error.HttpError, models.user.UserList]:
        requests = [self._users.detail(id) for id in {p.properties["author"] for p in predictions}]
        authors = await asyncio.gather(*requests)
        authors = helpers.combine_http_errors(authors)
        authors = authors.then(lambda a: models.user.UserList(users = a))
        return authors

    async def _prediction_countries(self, predictions: models.prediction.PredFeatureCollection):
        requests = [self._countries.detail(id) for id in {p.properties["country"] for p in predictions.features}]
        countries = await asyncio.gather(*requests)
        countries = helpers.combine_http_errors(countries)
        return countries.then(lambda ctries: [c.properties for c in ctries])

    async def _predictions_in_partition(self,
            country_id: Optional[int],
            schedule: models.time_partition.TimePartition
            ) -> Either[http_error.HttpError, models.prediction.PredFeatureCollection]:

        kwargs = {"start_date": schedule.start, "end_date":  schedule.end}
        kwargs = helpers.dictadd(kwargs, {"country": country_id}) if country_id is not None else kwargs

        predictions = await self._predictions.list(**kwargs)
        return predictions
