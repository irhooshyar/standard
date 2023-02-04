deactivate
 ..\evn\Scripts\activate
git checkout version3
git status
git pull
python manage.py makemigrations
python manage.py migrate --database En_DataBase
python manage.py migrate --database Fa_DataBase
python manage.py runserver