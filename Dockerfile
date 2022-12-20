FROM python:3.10-alpine3.15

WORKDIR /app/HW4

VOLUME [ "app/storage" ]

RUN pip install poetry


COPY ["poetry.lock", "pyproject.toml","/app/HW4/"]

RUN poetry config virtualenvs.create false

RUN poetry install


COPY . /app
WORKDIR /app

EXPOSE 3000 5000


CMD ["python", "HW4/main.py"]