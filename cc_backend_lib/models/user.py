import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

class UserIdentification(BaseModel):
    id:    int

class UserPersonIdentification(BaseModel):
    name:  Optional[str] = None
    email: Optional[str] = None

class UserParticipation(BaseModel):
    date_joined:        Optional[datetime.datetime] = None
    last_login:         Optional[datetime.datetime] = None
    assigned_countries: Optional[List[int]]         = None
    submitted_metadata: Optional[Dict[str, str]]    = None

class WaiverStatus(BaseModel):
    has_signed_waiver: Optional[bool] = None

class EmailStatus(BaseModel):
    has_unsubscribed: Optional[bool] = None

class EmailCooldownStatus(BaseModel):
    last_mailed: Optional[datetime.date] = None

class Scrubbable:
    class Meta:
        person_identifiable_fields = []

    @property
    def identifiable(self):
        for field in self.Meta.person_identifiable_fields:
            if getattr(self, field) is not None:
                return True
        return False

    def scrub(self):
        for field in self.Meta.person_identifiable_fields:
            setattr(self, field, None)


class UserDetail(
        UserIdentification,
        UserPersonIdentification,
        UserParticipation,
        Scrubbable,
        WaiverStatus,
        EmailStatus,
        EmailCooldownStatus):
    class Meta:
        person_identifiable_fields = [
                "name",
                "email",
                "date_joined",
                "last_login",
                "submitted_metadata"
            ]

class UserListed(UserIdentification, UserPersonIdentification, Scrubbable):
    class Meta:
        person_identifiable_fields = [
                "name",
                "email",
            ]

class UserList(BaseModel):
    users: List[UserListed]

    @property
    def identifiable(self):
        return any((u.identifiable for u in self.users))

    def scrub(self):
        for user in self.users:
            user.scrub()

class UserEmailStatus(UserIdentification, EmailStatus):
    """
    POSTed and GETed from the email subscription endpoint.
    """
