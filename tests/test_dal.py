
from typing import Optional
import asyncio
import unittest
import datetime
from geojson_pydantic import geometries
from pymonad.either import Left, Right
from cc_backend_lib import dal, models
from cc_backend_lib.clients import predictions_client, scheduler_client, users_client, countries_client
from cc_backend_lib.errors import http_error

def pred_feature(author_id: int, country_id: int):
    return models.prediction.PredictionFeature(
            geometry = geometries.Point(coordinates = [10,10]),
            properties = {
                    "intensity": 0,
                    "confidence": 0,
                    "author": author_id,
                    "country": country_id,
                    "date": "",
                    "casualties": "yeehaw"
                }
        )

class TestSummaries(unittest.TestCase):
    """
    TestSummaries
    =============

    Various tests of the summaries class, both with success and failure conditions.
    """
    def setUp(self):
        async def predictions(country: Optional[int] = None, *_,**__):
            features = [
                pred_feature(1,10),
                pred_feature(1,10),
                pred_feature(2,10),
                pred_feature(2,12),
                ]

            if country is not None:
                features = [f for f in features if f.properties["country"] == country]

            return Right(models.prediction.PredFeatureCollection(features = features))

        self.predictions = predictions_client.PredictionsClient("http://foo.bar.baz")
        self.predictions.list = predictions

        async def time_partition(*_,**__):
            return Right(models.time_partition.TimePartition(
                start = datetime.date(1000,9,10),
                end = datetime.date(1000,12,10),
                duration_months = 3
                ))

        self.scheduler                = scheduler_client.SchedulerClient("http://foo.bar.baz")
        self.scheduler.time_partition = time_partition

        async def user(id: int,*_,**__):
            return Right(models.user.User(id = id))

        self.users        = users_client.UsersClient("http://foo.bar.baz")
        self.users.detail = user

        async def country(id: int, *_,**__):
            return Right(models.country.Country(
                    geometry = geometries.Point(coordinates = [10,10]),
                    properties = {
                        "gwno": id,
                        "name": str(id),
                        "iso2c": str(id)
                        }
                    ))

        self.countries   = countries_client.CountriesClient("http://foo.bar.baz")
        self.countries.detail = country

        self.client = dal.Dal(
                predictions = self.predictions,
                scheduler   = self.scheduler,
                users       = self.users,
                countries   = self.countries,
            )

    def test_summaries_no_errors(self):
        summary = asyncio.run(self.client.participant_summary(country_id = 10))
        self.assertTrue(summary.is_right())
        self.assertEqual(summary.value.number_of_users, 2)

        summary = asyncio.run(self.client.participant_summary(country_id = 12))
        self.assertTrue(summary.is_right())
        self.assertEqual(summary.value.number_of_users, 1)

        summary = asyncio.run(self.client.participant_summary(country_id = 20))
        self.assertTrue(summary.is_right())
        self.assertEqual(summary.value.number_of_users, 0)

    def test_summaries_remote_500(self):
        async def fail(*_,**__):
            return Left(http_error.HttpError(http_code = 500, message = "Something went very wrong!!"))

        self.predictions.list = fail
        summary = asyncio.run(self.client.participant_summary(country_id = 1))
        self.assertTrue(summary.is_left())
        self.assertEqual(summary.monoid[0].http_code, 500)
        self.assertEqual(summary.monoid[0].message, "Something went very wrong!!")

    def test_countries_error(self):
        async def fail(*_, **__):
            return Left(http_error.HttpError(http_code = 404))
        self.countries.detail = fail

        summary = asyncio.run(self.client.participant_summary(country_id = 10))
        self.assertTrue(summary.is_left())
        self.assertEqual(summary.monoid[0].http_code, 404)

    def test_scheduler_error(self):
        async def fail(*_, **__):
            return Left(http_error.HttpError(http_code = 500))
        self.scheduler.time_partition = fail

        summary = asyncio.run(self.client.participant_summary(country_id = 1))
        self.assertTrue(summary.is_left())
        self.assertEqual(summary.monoid[0].http_code, 500)

    def test_participants(self):
        res = asyncio.run(self.client.participants())
        self.assertTrue(res.is_right())
        self.assertEqual({usr.id for usr in res.value.users},{1,2})

    def test_participants_failure(self):

        async def fail(id: int, *_, **__):
            return Left(http_error.HttpError(http_code = 404, message = f"User {id} not found"))

        self.users.detail = fail

        summary = asyncio.run(self.client.participants(country_id = 10))
        self.assertTrue(summary.is_left())
        self.assertEqual(summary.monoid[0].http_code, 404)
        self.assertEqual(len(summary.monoid[0].message.split("\n")), 2)

    def test_country_pred_summary(self):
        summary = asyncio.run(self.client.participant_summary()).value
        self.assertEqual({c.participants for c in summary.countries}, {2,1})
        self.assertEqual(summary.number_of_users, 2)
