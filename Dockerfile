FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./.env /code/.env
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install --upgrade pip
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-decouple psycopg2 python-multipart deepface face_recognition
# RUN pip freeze > requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]