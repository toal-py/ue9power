FROM python:3.12.0

# install cmake
#WORKDIR /root
#RUN mkdir temp
#WORKDIR /root/temp
#RUN curl -OL https://github.com/Kitware/CMake/releases/download/v3.27.4/cmake-3.27.4.tar.gz
#RUN tar -xzvf cmake-3.27.4.tar.gz

#WORKDIR /root/temp/cmake-3.27.4
#RUN ./bootstrap -- -DCMAKE_BUILD_TYPE:STRING=Release
#RUN make -j4
#RUN make install

#WORKDIR /root
#RUN rm -rf temp

COPY requirements.txt /dsh/

WORKDIR /dsh/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
COPY .env /var/www/python-project/ue9power/