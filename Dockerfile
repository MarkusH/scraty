FROM python:3.8-slim AS build

RUN mkdir -pv /src/deps

COPY . /src

WORKDIR /src

RUN pip download -d deps/ -r requirements.txt -r requirements-deploy.txt


FROM python:3.8-slim

LABEL maintainer="Markus Holtermann" \
      repository="MarkusH/scraty" \
      name="Scraty"
WORKDIR /src

RUN useradd -U -M gunicorn

EXPOSE 8000

COPY --from=build /src /src

WORKDIR /src

RUN pip install --no-deps /src/deps/*.whl \
      && rm -rf /src/deps

USER gunicorn:gunicorn

CMD ["gunicorn", "scraty.wsgi:application", "--user", "gunicorn", "--group", "gunicorn", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/dev/shm", "--log-level", "DEBUG", "--workers", "4"]
