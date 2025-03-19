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

### TESTS
cd backbase_test
 PYTHONPATH=$(pwd) python -m pytest --disable-warnings -v -s mycurrency/tests/test_*.py
