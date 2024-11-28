FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY .env /code/.env

COPY ./app /code/app

COPY ./.chainlit /code/.chainlit

CMD ["chainlit", "run" ,"app/main.py", "--host", "0.0.0.0"]