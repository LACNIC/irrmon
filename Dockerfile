FROM python:3.8-slim-buster
WORKDIR /usr/src/irrmon

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update
RUN apt upgrade -y 
RUN apt install whois -y 

COPY . .

CMD [ "python3", "./irrmon.py"]
