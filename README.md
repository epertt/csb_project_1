0. create and activate venv with CSB packages; install if needed; if you installed these outside of a venv you don't need to do this part
```
python3 -m pip install django requests
```
1. enter the directory with manage.py
2. run `python manage.py makemigrations pages`
3. run `python manage.py migrate`
4. run `python manage.py runserver`
5. go to http://localhost:8080/
