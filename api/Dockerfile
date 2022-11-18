FROM python:3.10

ENV POETRY_VERSION=1.1.8
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /api
COPY . /api/

RUN poetry install

CMD /bin/sh -c "poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000"
