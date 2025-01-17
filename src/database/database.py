#!/usr/bin/env python3

from socket import socket
import sys
from typing import Any
from rich.console import Console
from threading import Thread
import yaml

##### Colors
TXT_INFO: str = "yellow"
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"


##### DATABASE LOGIC #####
# Read the database and return the contents as a string
def read_database(conn: socket, address: tuple, args: any) -> None:
    database_name: str = args[0]

    console.log(f"{address} asked for the database '{database_name}'", style=TXT_INFO)
    with open(f"{database_name}.yaml", "r") as f:
        database_content: list = yaml.load(f, Loader=yaml.FullLoader) # loads the yaml file into a list.
    f.close()
    database_content: str = str(database_content) # Changes the list into a string
    conn.sendall(database_content.encode()) # Sends the database content as a string to the server connection

# Append the content to the database
def append_database(_: any, address: tuple, args: any) -> None:
    database_name: str = args[0]
    content: str = args[1]

    console.log(f"{address} appended {content} to the database '{database_name}'", style=TXT_INFO)
    with open(f"{database_name}.yaml", "a") as f:
        yaml.dump([eval(content)], f, default_flow_style=False, allow_unicode=True) # 'Dumps' the information the database has
        # received into the yaml file.
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
        client_input: bytes = conn.recv(8024)

        if client_input:
            client_input_decoded: str = client_input.decode()
            command: str; args: str
            command, args = (client_input_decoded + " ").split(" ", 1)
            args = args.strip().split(" ", 1)

            # If command exists and the command has an argument
            if command in commands and args:
                commands[command](conn, address, args)
            else:
                console.log(f"{address}, sent a command that does not exist: [{command}, {args}]", style=TXT_INFO)
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

# Rich
console = Console()

if __name__ == "__main__":
    HOST: str; PORT: int
    PORT = 8888
    if "docker" in sys.argv:
        HOST = "database"
    else:
        HOST = "localhost"

    sock = socket() # sets up a socket connection with the server
    sock.bind((HOST, PORT))
    sock.listen()

    console.print(f"Starting database server on {HOST}:{PORT}", style="bold red")

    accept(sock)

    console.print("Stopping server")
    sock.close()
