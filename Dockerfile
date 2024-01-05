FROM python:3.10

ENV HOST="http://localhost:5000"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]