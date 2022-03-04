#!/usr/bin/env python3

from socket import socket
from typing import Any
from rich.console import Console
from threading import Thread
import yaml

##### Colors
TXT_INFO: str = "bold yellow"
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"


##### DATABASE LOGIC #####
# Read the database and return the contents as a string
def read_database(conn: socket, address: tuple, database_name: str) -> None:
    console.log(f"{address} asked for the database '{database_name}'", style=TXT_INFO)
    with open(f"{database_name}.yaml", "r") as f:
        database_content: list = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    database_content: str = str(database_content)
    conn.sendall(database_content.encode())

# Append the content to the database
def append_database(database_name: str, content: str) -> None:
    with open(f"{database_name}.yaml", "a") as f:
        pass # Logic here
    f.close()

##### SOCKET LOGIC #####
# Accept incoming connections
def accept(sock: str) -> None:
    while True:
        conn: str; address: tuple
        conn, address = sock.accept()
        console.log(f"Server {address} has connected.", style=TXT_CONN)
        Thread(target=read, args=(conn, address)).start()

# Read the incoming connections
def read(conn: socket, address: tuple) -> None:
    while True:
        client_input: bytes = conn.recv(1024)

        if client_input:
            client_input_decoded: str = client_input.decode()
            command: str; arg: str
            command, arg = (client_input_decoded + " ").split(" ", 1)
            arg = " ".join(arg.strip().split(" "))

            # If command exists and the command has an argument
            if command in commands and arg:
                commands[command](conn, address,  arg)
            else:
                console.log(f"{address}, sent a command that does not exist: [{command}, {arg}]", style="bold yellow")
        else:
            console.log(f"{address} has disconnected.", style=TXT_DCON)
            conn.close()
            break

##### MAIN #####
# Commands that can be used
commands: dict[str, Any] = {
    "read_database": read_database,
    "append_database": append_database
}

# Host and port
HOST: str = ""
PORT: int = 8888

# Rich
console = Console()

if __name__ == "__main__":
    sock = socket()
    sock.bind((HOST, PORT))
    sock.listen()

    console.print(f"Starting database server on {HOST}:{PORT}", style="bold red")

    accept(sock)

    console.print("Stopping server")
    sock.close()