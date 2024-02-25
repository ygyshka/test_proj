FROM python:3.11

WORKDIR /code

COPY ./poetry.lock pyproject.toml /code/

RUN pip3 install --no-cache-dir poetry==1.7.1
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/