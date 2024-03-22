FROM python:3.12.0

COPY requirements.txt /dsh/

WORKDIR /dsh/

RUN apt-get install cmake
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .