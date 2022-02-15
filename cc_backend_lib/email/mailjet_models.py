
from typing import List, Optional, Dict
import pydantic

class Contact(pydantic.BaseModel):
    Email: pydantic.EmailStr
    Name:  str

class Message(pydantic.BaseModel):
    From:             Contact
    To:               List[Contact]
    Subject:          str
    TextPart:         Optional[str]           = None
    HTMLPart:         Optional[str]           = None
    TemplateID:       Optional[int]           = None
    Variables:        Optional[Dict[str,str]] = None
    TemplateLanguage: bool                    = False


class SendData(pydantic.BaseModel):
    Messages: List[Message]
