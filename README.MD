### Django Friendlier service
___

* create **venv** (python -m venv venv)
* source venv/Scripts/activate
* `pip install -r requirements.txt`
* `python manage.py makemigraitions main`
* `python manage.py migrate`
* `python manage.py runserver`

После перейти на __http://127.0.0.1:8000/redoc/__ скачать openapi.json

Либо сразу отсюда __http://127.0.0.1:8000/redoc/?format=openapi__

Загрузить json в postman

---

#
### Docker


* `docker build -t django_project:v1 .`
* `docker run --name backend -p 8000:8000 django_project:v1`
