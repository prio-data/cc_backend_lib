
# CC Backend Library 

![tests status](https://github.com/prio-data/cc_backend_lib/actions/workflows/test.yml/badge.svg)

This library contains several classes and data models that are useful when
writing services that interact with other services in Conflict Cartographer. In
particular, the modules `api_client` and `schema` respectively provide classes
for retrieving and modelling data from APIs.

## Data retrieval

Data retrieval is offered via the `cc_backend_lib.dal.Dal` class. This class is
instantiated by passing several API clients: 

```
from cc_backend_lib.clients import predictions_client, scheduler_client, users_client, countries_client
from cc_backend_lib import dal

cc_dal = dal.Dal(
      predictions = predictions_client.PredictionsClient(...),
      scheduler = scheduler_client.SchedulerClient(...),
      users = users_client.UsersClient(...),
      countries = countries_client.CountriesClient(...),
   )
```

The class has several methods that offer access to data and summaries. See `help(Dal)`
