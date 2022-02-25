FROM python:3.10.2-bullseye
WORKDIR /src
COPY /src /src
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r requirements.txt
COPY . /src
CMD [ "python3", "main.py" ]