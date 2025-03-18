FROM python:3-alpine3.12

RUN addgroup -S app
RUN adduser -S app -G app

USER app:app

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
