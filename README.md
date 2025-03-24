### INSTALL APP
#### Local Installation
Follow these steps after having python3.11 installed:
```
cd backbase_test/
python3.11 -m venv venv
source venv/bin/activate 
pip install --upgrade pip
pip install -r mycurrency/requirements.txt
```
#### Docker installation
Follow these steps only if you have docker running in your system:
```
cd backbase_test/mycurrency
docker build -t mycurrency . 
docker run -p 8000:8000 mycurrency
```

### INIT MYCURRENCY APP

1. Run the following commands to load migrations, create an admin user and run de server (skip this step if using Docker):
```
PYTHONPATH=$(pwd) python mycurrency/manage.py migrate
PYTHONPATH=$(pwd) python mycurrency/manage.py createsuperuser
PYTHONPATH=$(pwd) python mycurrency/manage.py runserver
```

2. Using the admin page, set the Private key for the CurrencyBacon provider
- Assuming that MyCurrency app will be running in localhost and using port 8000:
- Open http://127.0.0.1:8000/admin/ in a browser and connect using the admin user previously created
Note: Docker uses user 'backbase' with the same password
- Update CurrencyBacon provider: Home > Providers > CurrencyBacon

#### MANAGE PROVIDERS
```
You can enable/disable and change provider's priority here:
http://127.0.0.1:8000/admin/rates/provider/
```

#### TEST THE ENDPOINTS
You can use rates/postman_collections/JOBS_BackBase.postman_collection.json and import them using Postman

- CURRENCY RATES
```
Method      Endpoint                        Example
GET         /api/v1/currency-rates/         http://127.0.0.1:8000/api/v1/currency-rates/?source_currency=USD&date_from=2025-01-01&date_to=2025-01-10
```

- CURRENCY CONVERTER: 
```
Method      Endpoint                        Example
GET         /api/v1/currency-converter/     http://127.0.0.1:8000/api/v1/currency-converter/?source_currency=USD&exchanged_currency=GBP&amount=1
```

- FETCHING MASSIVE HISTORY RATES (concurrency way)
```
Method      Endpoint                        Example
POST        /api/v1/currency-history-rates/ http://127.0.0.1:8000/api/v1/currency-history-rates
                                            Body:
                                            {
                                                "source_currency": "USD",
                                                "date_from": "2000-01-01",
                                                "date_to": "2025-03-15"
                                            }
                                            Response:
                                            {
                                                "process_id": "6f13c39a-3584-4f30-b1b5-4ae41e7bfd31"
                                            }
You can follow the batch process here:
http://127.0.0.1:8000/admin/rates/batchprocess/

Note:
- Parallelism is discarted when fetching massive data to avoid being banned from remote API providers
- Smart fetching: only missing rates from data base will be request from data provider
- A minor 0.2 second delay is add to each request
```

- CURRENCY CRUD:
```
Method      Endpoint                Description
GET         /api/currency-rates/        Retrieve a time serie convertion rate based on date range 
GET         /api/currency-converter/    Convert a courrency amount
GET         /api/currency/              List all currencies
POST        /api/currency/              Create a new currency
GET         /api/currency/{id}/         Retrieve a specific currency
PUT         /api/currency/{id}/         Update a currency
PATCH       /api/currency/{id}/         Partially update a currency
DELETE      /api/currency/{id}/         Delete a currency
````

- API Version
```
Method      Endpoint            Description
GET         /api/version/       Shows current API version
```

### CONVERT MANY CURRENCIES AT THE SAME TIME
```
Use this separate form to submit your queries
http://127.0.0.1:8000/converter/
```

### RUN TESTS
```
cd backbase_test
PYTHONPATH=$(pwd) python -m pytest --disable-warnings -v -s mycurrency/tests/test_*.py
```
