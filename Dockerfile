FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./.env /code/.env
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install --upgrade pip
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install fastapi uvicorn[standard] python-decouple psycopg2 python-multipart
RUN pip install --no-cache-dir deepface face_recognition
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]