FROM python:3.10.2-bullseye
COPY . .
RUN pip3 install -r requirements.txt
ENV TERM xterm-256color
CMD [ "python3", "client.py" ]
