FROM python:3

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app
EXPOSE 3030
CMD ["python3", "master.py"]
