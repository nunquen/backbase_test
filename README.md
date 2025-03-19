### INSTALL APP
```
cd backbase_test/
python3.11 -m venv venv
source venv/bin/activate 
pip install --upgrade pip
pip install -r requirements.txt
```

PYTHONPATH=$(pwd) python mycurrency/manage.py makemigrations
PYTHONPATH=$(pwd) python mycurrency/manage.py migrate
PYTHONPATH=$(pwd) python mycurrency/manage.py createsuperuser
PYTHONPATH=$(pwd) python mycurrency/manage.py runserver


### Endpoints
- CURRENCE RATES
GET         /currency-rates/?source_currency=USD&date_from=2025-01-06&date_to=2025-01-25

- Currency CRUD
Method      Endpoint            Description
GET         /currency/          List all currencies
POST        /currency/          Create a new currency
GET         /currency/{id}/     Retrieve a specific currency
PUT         /currency/{id}/     Update a currency
PATCH       /currency/{id}/     Partially update a currency
DELETE      /currency/{id}/     Delete a currency



### TESTS
cd backbase_test
PYTHONPATH=$(pwd) python -m pytest --disable-warnings -v -s mycurrency/tests/test_*.py
