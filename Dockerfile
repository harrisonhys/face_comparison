FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./.env /code/.env
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn[standard] tf-keras python-decouple psycopg2-binary python-multipart deepface
COPY ./app /code/app
RUN mkdir /code/app/photos
RUN mkdir /code/app/photos_compare
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]