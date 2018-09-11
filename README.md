# Sensor application

Setup instructions:


* install Python 3.6.5 or 3.7.0

* create a virtual environment:
```
python -m venv ~/py_virtual_env/backend
```

* activate the virtual environment:
 ```
 source ~/py_virtual_env/backend/bin/activate
 ```

* install requirements:
```
cd backend && pip install -r requirements.txt
```

install and start redis-server
```
e.g. brew install redis && brew services start redis
if you're on OS X
```


Database setup:

* go to root directory and run the script:
```
python create_iot_db.py
```
now there should be an sqlite database file in the root directory, move it to backend directory instead:
```
mv iot_db.sqlite backend
```

* run migrations required by django models:
```
python manage.py migrate
```


* run script to populate redis cache:
```
python manage.py hard_reset_statistics
```

Now most of the setup is done.

To run tests:
```
python manage.py test
```

Run celery worker and beat in 2 terminal tabs:
(Note: these need to be ran before temperature difference data will be available from the frontend)
```
celery -A backend beat -l info
celery -A backend worker -l info
```

To create a user
(follow the instructions in the command line):
```
python manage.py createsuperuser
```

Now you can run django server(this will start a server on port 8000):

```
python manage.py runserver
```
