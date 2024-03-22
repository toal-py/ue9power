FROM python:3.12.0

COPY requirements.txt /dsh/

WORKDIR /dsh/

RUN apt install build-essentials
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .