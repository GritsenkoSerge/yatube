FROM python:3.7-slim

RUN python3 -m pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "yatube.wsgi:application", "--bind", "0:8000"]