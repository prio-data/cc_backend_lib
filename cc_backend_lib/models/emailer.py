"""
emailer

Data models related to the cc_emailer service.
"""

from typing import Optional, List
from pydantic import BaseModel
from . import time_partition, user, country, prediction

class ParticipationSummary(BaseModel):
    """
    ParticipationSummary
    ====================

    parameters:
        number_of_users (int): The number of users who participated
        partition: (cc_backend_lib.models.time_partition.TimePartition)
        country_id (Optional[int]): Subset by country

    A summary of how many users participated in a given TimePartition,
    optionally subset by country_id.
    """
    number_of_users: int
    partition: time_partition.TimePartition
    countries: List[country.CountryProperties]

    @classmethod
    def from_user_list(
            cls: "ParticipationSummary",
            user_list: user.UserList,
            partition: time_partition.TimePartition,
            countries: List[country.CountryProperties]) -> "ParticipationSummary":
        """
        from_user_list
        """

        return cls(
            number_of_users = len(user_list.users),
            partition       = partition,
            countries       = countries)

class EmailSpecification(BaseModel):
    """
    EmailSpecification
    ==================

    Posted by an admin user as a request to send emails to users that
    participated in the specified time / country combination.
    """

    shift: int
    countries: List[int]
    content: Optional[str] = None
    template: Optional[int] = None
