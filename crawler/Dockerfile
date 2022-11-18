FROM python:3.10 AS crawler

ENV POETRY_VERSION=1.2.2
ENV PATH="/usr/local/bin:$PATH"
# Might not be needed^^^

RUN python -m pip install pip==22.3.1
RUN python -m pip install poetry==$POETRY_VERSION

WORKDIR /crawler/
COPY poetry.lock pyproject.toml /crawler/

RUN poetry install

COPY . /crawler/

CMD /bin/sh -c "poetry run python /crawler/crawler/main.py"

FROM crawler AS alembic

COPY --from=crawler /crawler /crawler
WORKDIR /crawler/

RUN poetry install --with alembic

WORKDIR /crawler/crawler/

CMD /bin/sh -c "poetry run alembic upgrade head"

FROM crawler AS test
