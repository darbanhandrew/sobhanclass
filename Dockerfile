FROM python:3.9.0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential \
    && apt-get install -y gcc\
    # psycopg2 dependencies
    && apt-get install -y libpq-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/