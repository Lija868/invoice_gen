Steps
1. Clone the project
2. activate the virtual environment (python -m venv venv)
3. install the requirements (pip install -r requirements.txt)
4. replace the values in config.py.sample(db credentials)
5. migrate commands 

    python manage.py makemigrations
    
    python manage.py migrate
6. create super user

    python manage.py createsuperuser
7. run the server

    python manage.py runserver
api doc link : https://documenter.getpostman.com/view/12173007/TzzGFtEP
to load the data, got to django admin and select invoice table and hit loaddata button
