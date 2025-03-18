FROM python:3.9

WORKDIR /app

COPY challenge/requirements.txt ./requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./challenge .

EXPOSE 8000

CMD ["fastapi", "run", "app.py", "--port", "8000"]