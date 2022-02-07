
import datetime
from typing import List,Dict,Union,Any, Optional
from pydantic import BaseModel
from geojson_pydantic import features
from . import scales

class PredictionProperties(BaseModel):
    intensity: int
    confidence: int
    author: int
    country: int
    date: datetime.date
    casualties: scales.CasualtyRange

class PredictionFeature(features.Feature):
    class Meta:
        QUERY_ORDER = ["id","shape","values","author_id","country_id","date"]
    properties: Dict[str,Union[int,float,scales.CasualtyRange,datetime.date,str]] #PredictionProperties

    @classmethod
    def from_row(cls,id,shape,values,author_id,country_id,date,*_,**__):
        return cls(
            geometry = shape["geometry"],
            properties = {
                    "intensity": values["intensity"],
                    "confidence": values["confidence"],
                    "author": author_id,
                    "country": country_id,
                    "date": date,
                    "casualties": scales.scaled(date,values["intensity"])
                },
            id=id
        )

class PredFeatureCollection(features.FeatureCollection):
    features: List[PredictionFeature]

    @classmethod
    def from_response(cls,rows):
        return cls(
                features = [PredictionFeature.from_row(**dict(r)) for r in rows]
            )

class CountryProperties(BaseModel):
    gwno: int
    name: str
    iso2c: str

class CountryFeature(features.Feature):
    class Meta:
        QUERY_ORDER = ["gwno","name","iso2c","shape"]

    properties: CountryProperties

    @classmethod
    def from_row(cls,gwno,name,iso2c,shape):
        return cls(
                geometry = shape,
                properties = CountryProperties(
                        gwno = gwno,
                        name = name,
                        iso2c = iso2c
                    )
                )

class NonAnswer(BaseModel):
    class Meta:
        QUERY_ORDER = ["country_id","author_id","date"]

    gwno: int
    author: int
    date: datetime.date

    @classmethod
    def from_row(cls,gwno,author,date):
        return cls(
                gwno = gwno,
                author = author,
                date = date

            )

class QuarterlyData(BaseModel):
    year: int
    quarter: int
    data: List[Any]

class PredictionsSummary(BaseModel):
    confidence: float
    intensity: float
    accuracy: Optional[float]
    coverage: Optional[float]
    gwno: Optional[int]
    @property
    def evaluated(self):
        return self.accuracy is not None and self.coverage is not None

class QuarterlyPredictionSummary(QuarterlyData):
    data: List[PredictionsSummary]
