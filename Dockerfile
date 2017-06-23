FROM python:2.7-slim

WORKDIR /app
ADD depencies /app/depencies/
ADD config /app/config/
ADD server.py /app

RUN apt-get update -y
RUN apt install python-pip default-jre -y
RUN pip install pymongo flask requests werkzeug 
RUN mkdir /app/tmp_data

EXPOSE 80

CMD ["python", "server.py"]
