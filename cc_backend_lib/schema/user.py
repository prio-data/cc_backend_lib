import datetime
from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    id:          int
    name:    Optional[str]
    email:       Optional[str]
    date_joined: Optional[datetime.datetime]
    last_login:  Optional[datetime.datetime]

    @property
    def identifiable(self):
        return self.name is None and self.email is None

    def scrub(self):
        self.name = None
        self.email = None

class UserList(BaseModel):
    users: List[User]

    @property
    def identifiable(self):
        return any((u.identifiable for u in self.users))

    def scrub(self):
        for user in self.users:
            user.scrub()
