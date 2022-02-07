
import json
import pydantic
from pymonad.either import Either, Right, Left
from cc_backend_lib import models
from cc_backend_lib.errors import http_error
from . import model_api_client

class CountriesClient(model_api_client.ModelApiClient[models.country.Country, models.country.CountryPropertiesList]):

    def deserialize_detail(self, data:bytes) -> Either[http_error.HttpError, models.country.Country]:
        try:
            return Right(models.country.Country(**json.loads(data)))
        except (json.JSONDecodeError, pydantic.ValidationError) as err:
            return Left(http_error.HttpError(message = str(err), http_code = 500))

    def deserialize_list(self, data:bytes) -> Either[http_error.HttpError, models.country.CountryPropertiesList]:
        try:
            return Right(models.country.CountryPropertiesList(
                    countries = json.loads(data)
                    ))
        except (json.JSONDecodeError, pydantic.ValidationError) as err:
            return Left(http_error.HttpError(message = str(err), http_code = 500))
