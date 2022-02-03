"""
The intensity measurement scale has changed, and might change again
Therefore, I need this module to translate between numeric intensity scores
and casualty numbers
"""
from typing import Optional
from datetime import date
import pydantic

class CasualtyRange(pydantic.BaseModel):
    lower: int
    upper: Optional[int]
    text: Optional[str]

    @property
    def zero(self):
        return self.upper == 0

SCALES = {
    # The old scale
    date(1,1,1):{
            0: CasualtyRange(lower=0,upper=1),
            1: CasualtyRange(lower=2,upper=25),
            2: CasualtyRange(lower=26,upper=99),
            3: CasualtyRange(lower=100,upper=999),
            4: CasualtyRange(lower=1000,upper=None),
        },
    # The current scale
    date(2021,1,1):{
            0: CasualtyRange(lower=1,upper=25,text="Low"),
            1: CasualtyRange(lower=26,upper=99,text="Medium"),
            2: CasualtyRange(lower=100,upper=None,text="High"),
        }
}

def scaled(date:date,intensity_value:int)->CasualtyRange:
    if intensity_value < 0:
        return CasualtyRange(lower=0,upper=0)
    valid_scales = {k:v for k,v in SCALES.items() if k <= date}
    scale_for_date = SCALES[max((d for d,_ in valid_scales.items()))]
    return scale_for_date[intensity_value]
