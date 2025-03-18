
python3.11 -m venv venv
source venv/bin/activate 
pip install --upgrade pip
pip install -r requirements.txt

cd backbase/
PYTHONPATH=$(pwd) python mycurrency/manage.py migrate
PYTHONPATH=$(pwd) python mycurrency/manage.py createsuperuser
PYTHONPATH=$(pwd) python mycurrency/manage.py runserver