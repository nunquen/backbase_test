### INSTALL APP
Follow these steps after having python3.11 installed:
```
cd backbase_test/
python3.11 -m venv venv
source venv/bin/activate 
pip install --upgrade pip
pip install -r requirements.txt
```

### INIT MYCURRENCY APP
1. Run the following commands to load migrations, create an admin user and run de server:
```
PYTHONPATH=$(pwd) python mycurrency/manage.py migrate
PYTHONPATH=$(pwd) python mycurrency/manage.py createsuperuser
PYTHONPATH=$(pwd) python mycurrency/manage.py runserver
```

2. Using the admin page, set the Private key for the CurrencyBacon provider
- Assuming that MyCurrency app will be running in localhost and using port 8000:
- Open http://127.0.0.1:8000/admin/ in a browser and connect using the admin user previously created
- Update CurrencyBacon provider: Home > Providers > CurrencyBacon

#### TEST THE ENDPOINTS
You can use rates/postman_collections/JOBS_BackBase.postman_collection.json and import them using Postman

- CURRENCY RATES [GET]: /api/v1/currency-rates/?source_currency=USD&date_from=2025-01-06&date_to=2025-01-25

- CURRENCY CONVERTER [GET]: /api/v1/currency-converter/?source_currency=USD&exchanged_currency=GBP&amount=1

- Currency CRUD:
```
Method      Endpoint            Description
GET         /currency/          List all currencies
POST        /currency/          Create a new currency
GET         /currency/{id}/     Retrieve a specific currency
PUT         /currency/{id}/     Update a currency
PATCH       /currency/{id}/     Partially update a currency
DELETE      /currency/{id}/     Delete a currency
````

- API Version
```
Method      Endpoint            Description
GET         /api/version/       Shows current API version
```

### RUN TESTS
cd backbase_test
PYTHONPATH=$(pwd) python -m pytest --disable-warnings -v -s mycurrency/tests/test_*.py




PYTHONPATH=$(pwd) python mycurrency/manage.py makemigrations
PYTHONPATH=$(pwd) python mycurrency/manage.py migrate
PYTHONPATH=$(pwd) python mycurrency/manage.py createsuperuser
PYTHONPATH=$(pwd) python mycurrency/manage.py runserver
