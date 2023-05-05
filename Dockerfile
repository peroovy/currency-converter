FROM python:3.10-alpine3.17

WORKDIR /app

RUN apk update && \
    apk add make

COPY Pipfile* .

RUN pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile

COPY . .

CMD ["gunicorn", "app.main:create_app", "-w", "4", "--worker-class", "aiohttp.worker.GunicornWebWorker", "--bind", ":8000"]