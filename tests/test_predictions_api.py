import asyncio
import unittest
import aioresponses
from geojson_pydantic import geometries
from cc_backend_lib.clients import predictions_client
from cc_backend_lib import models 

class TestPredictionsApi(unittest.TestCase):

    def test_list_success(self):
        with aioresponses.aioresponses() as m:
            m.get("/shapes/", payload = models.prediction.PredFeatureCollection(features = []).dict())
            client = predictions_client.PredictionsClient("http://foo.bar","shapes")
            result = asyncio.run(client.list())
            self.assertTrue(result.is_right())

    def test_detail_success(self):
        with aioresponses.aioresponses() as m:
            m.get("/shapes/1/", payload = models.prediction.PredictionFeature(properties = {}, geometry = geometries.Point(coordinates = [1,1])).dict())
            client = predictions_client.PredictionsClient("http://foo.bar","shapes")
            result = asyncio.run(client.detail("1"))
            self.assertTrue(result.is_right())

    def test_bad_data_failure(self):
        with aioresponses.aioresponses() as m:
            m.get("/shapes/", payload = {"junk":"data"})
            m.get("/shapes/1/", payload = {"junk":"data"})

            client = predictions_client.PredictionsClient("http://foo.bar","shapes")
            result = asyncio.run(client.list())
            self.assertTrue(result.is_left())
            self.assertEqual(result.either(lambda x:x, lambda x:x).http_code, 500)

            result = asyncio.run(client.detail("1"))
            self.assertTrue(result.is_left())
            self.assertEqual(result.either(lambda x:x, lambda x:x).http_code, 500)

    def test_notfound(self):
        with aioresponses.aioresponses() as m:
            m.get("/shapes/1/", status = 404)
            client = predictions_client.PredictionsClient("http://foo.bar","shapes")
            result = asyncio.run(client.detail("1"))
            self.assertTrue(result.is_left())
            self.assertEqual(result.either(lambda x:x, lambda x:x).http_code, 404)
