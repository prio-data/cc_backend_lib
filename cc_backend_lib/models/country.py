
from typing import List, Optional
from pydantic import BaseModel
from geojson_pydantic import features, geometries

class Country(features.Feature):
    class Meta:
        QUERY_ORDER = ["gwno","name","iso2c","shape"]

    properties: "CountryProperties"

    @classmethod
    def from_row(cls,
            gwno: int,
            name: str,
            iso2c: str,
            shape: geometries.Geometry):
        return cls(
                geometry = shape,
                properties = CountryProperties(
                        gwno = gwno,
                        name = name,
                        iso2c = iso2c
                    ),
                id = gwno
                )

class CountryIdentity(BaseModel):
    gwno: int
    name: str

class CountryProperties(CountryIdentity):
    iso2c:       Optional[str] = None
    predictions: Optional[int] = None
    participants:Optional[int] = None

class CountryPropertiesList(BaseModel):
    countries: List[CountryProperties]

class CountryList(BaseModel):
    countries: List[CountryIdentity]

Country.update_forward_refs()
