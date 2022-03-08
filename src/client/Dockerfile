FROM python:3.10.2-bullseye
COPY . .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
ENV TERM xterm-256color
CMD [ "python3", "client.py", "docker"]
