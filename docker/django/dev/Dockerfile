FROM python:3.7.5
ARG LOAD_MODELS


WORKDIR /app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
COPY requirements_AI.txt /app/requirements_AI.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt --retries 20
RUN --mount=type=cache,target=/root/.cache/pip if $LOAD_MODELS ; then pip install -r requirements_AI.txt --retries 20; fi;
RUN python -m spacy download en_core_web_sm
# RUN apt-get install chromium -y

# create aliases
RUN echo '#! /bin/sh' >> /bin/pmmm
RUN echo 'python manage.py makemigrations' >> /bin/pmmm
RUN chmod u+x /bin/pmmm
# RUN echo 'alias pmmm="python manage.py makemigrations"' >> ~/.bashrc

RUN echo '#! /bin/sh' >> /bin/pmcm
RUN echo 'python manage.py shell < ./docker/django/clean_migrations.py; rm -rf ./doc/migrations/; python manage.py migrate --database=Fa_DataBase --fake; python manage.py migrate --database=En_DataBase --fake; python manage.py makemigrations doc; python manage.py migrate --database=Fa_DataBase --fake-initial; python manage.py migrate --database=En_DataBase --fake-initial' >> /bin/pmcm
RUN chmod u+x /bin/pmcm
# RUN echo 'alias pmcm="python manage.py shell < ./docker/django/clean_migrations.py; rm -rf ./doc/migrations/; python manage.py migrate --database=Fa_DataBase --fake; python manage.py migrate --database=En_DataBase --fake; python manage.py makemigrations doc; python manage.py migrate --database=Fa_DataBase --fake-initial; python manage.py migrate --database=En_DataBase --fake-initial"' >> ~/.bashrc

RUN echo '#! /bin/sh' >> /bin/pmm
RUN echo 'python manage.py migrate' >> /bin/pmm
RUN chmod u+x /bin/pmm
# RUN echo 'alias pmm="python manage.py migrate"' >> ~/.bashrc

RUN echo '#! /bin/sh' >> /bin/pmm-fa
RUN echo 'python manage.py migrate --database=Fa_DataBase' >> /bin/pmm-fa
RUN chmod u+x /bin/pmm-fa
# RUN echo 'alias pmm-fa="python manage.py migrate --database=Fa_DataBase"' >> ~/.bashrc

RUN echo '#! /bin/sh' >> /bin/pmm-en
RUN echo 'python manage.py migrate --database=En_DataBase' >> /bin/pmm-en
RUN chmod u+x /bin/pmm-en
# RUN echo 'alias pmm-en="python manage.py migrate --database=En_DataBase"' >> ~/.bashrc

# Now copy in our code, and run it
COPY . /app


RUN if $LOAD_MODELS ; then python -c 'from doc.huggingface_views import *'; fi;


#RUN python manage.py shell < ./docker/django/clean_migrations.py
#RUN rm -rf ./doc/migrations/
#RUN python manage.py migrate --database=Fa_DataBase --fake
#RUN python manage.py migrate --database=En_DataBase --fake
#RUN python manage.py makemigrations doc
#RUN python manage.py migrate --database=Fa_DataBase --fake-initial
#RUN python manage.py migrate --database=En_DataBase --fake-initial