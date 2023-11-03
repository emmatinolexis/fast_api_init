FROM python:3.9
WORKDIR /mvtracking

COPY ./requirements.txt /mvtracking/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /mvtracking/requirements.txt

COPY ./app /mvtracking/app

ENV DB_USER mvistaging
ENV DB_PASSWORD mv15t%40g3db45Ag3
ENV DB_HOST 15.236.33.216
ENV DB_PORT 5432
ENV DB_NAME mvi_staging_db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]