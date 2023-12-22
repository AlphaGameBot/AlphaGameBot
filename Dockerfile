FROM python:3.11.2

WORKDIR /docker
COPY requirements.txt /docker/requirements.txt
RUN /usr/local/bin/python3 -m pip install -r /docker/requirements.txt
COPY . /docker

CMD ["python3", "/docker/main.py"]