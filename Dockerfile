FROM python:3.10.2-bullseye
COPY . /team-local-tactics
RUN pip3 install -r /team-local-tactics/requirements.txt
ENV TERM xterm-256color
CMD [ "python3", "/team-local-tactics/src/main.py" ]
