#!/usr/bin/env python3

from socket import socket, create_connection
from threading import Thread
from rich.console import Console
from time import sleep
from game_logic import Match, Team
import numpy as np
from os import getcwd


##### DATABASE LOGIC
# Reading the data base
def get_database(conn: socket, database_name: str, reciver="client") -> None:
    db_conn.sendall(f"read_database {database_name}".encode())
    db_response: str = db_conn.recv(8024).decode()
    if reciver == "client":
        conn.sendall(db_response.encode())
    else:
        return eval(db_response)


##### PLAYING TEAM LOCAL TACTICS
# A lobby, when a client is waiting for a game
def start_lobby(conn: socket, name: str) -> None:
    ### How lobby is structured
    # [0] is the players connection
    # [1] is the players name
    # [2] is the players champions
    ###
    lobby.append((conn, name, []))
    console.log(f"'{name}' joined the game lobby. ({len(lobby)}/2)", style=TXT_INFO)

    while len(lobby) < 2:
        sleep(1)
    else:
        conn.sendall("lobby_found".encode())
        
        console.log(f"Lobby full - {[player[1] for player in lobby]}")



def add_champion(conn: socket, champion: str) -> None:
    for player in lobby:
        if player[0] == conn:
            player[2].append(eval(champion))
            console.log(f"{player[1]} has: {player[2]}")


def total_picked(conn: socket) -> None:
    n: int = 0
    

    for player in lobby:
        n += len(player[2])

    conn.send(f"{n}".encode())


def get_lobby(conn: socket) -> None:
    lobby_to_send: list = []
    for player in lobby:
        lobby_to_send.append(player[1:])

    conn.send(f"{lobby_to_send}".encode())

def whoami(conn: socket):
    found: bool = False
    for id, player in enumerate(lobby):
        if conn == player[0]:
            conn.send(f"{id}".encode())
            found = True
    
    if not found:
        conn.sendall(f"{len(lobby) + 1}".encode())


def get_turn(conn: socket):
    picks_left = 4 - (len(lobby[0][2]) + len(lobby[1][2]))

    console.log(f"Picks left: {picks_left}", style=TXT_INFO)

    console.log(f"{picks_left % 2}", style=TXT_INFO)
    conn.send(f"{picks_left % 2}".encode())

def remove_from_lobby(player_to_remove: socket, address: tuple) -> None:
    for player in lobby:
        if player[0] == player_to_remove:
            lobby.remove(player)
            console.log(f"{address} has been removed from the lobby.", style=TXT_INFO)
    console.log(f"Lobby: {len(lobby)}/2", style=TXT_INFO)

##### SOCKET LOGIC #####
# Accept incoming connections
def accept(sock: str) -> None:
    while True:
        conn: str; address: tuple
        conn, address = sock.accept() 
        console.log(f"Client {address} has connected", style=TXT_CONN)
        Thread(target=read, args=(conn, address)).start()

# Read the incoming connections
def read(conn: socket, address: tuple) -> None:
    while True:
        client_input: bytes = conn.recv(1024)
        
        if client_input:
            client_input_decoded: str = (client_input.decode() + " ").split(" ", 1)
            command: str = client_input_decoded[0].strip()
            args: str = client_input_decoded[1].strip()

            console.log(f"{address} sent: [{command, args}]", style=TXT_INFO)

            if command in commands:
                if args:
                    commands[command](conn, args)
                else:
                    commands[command](conn)
            else:
                console.log("AN UNKNOWN COMMAND WAS SENT!", style=TXT_DCON)

        else:
            console.log(f"Client {address} has disconnected", style=TXT_DCON)
            remove_from_lobby(conn, address)
            conn.close()
            break


##### MAIN #####

commands: dict = {
    "get_database": get_database,
    "start_lobby": start_lobby,
    "add_champion": add_champion,
    "total_picked": total_picked,
    "whoami": whoami,
    "get_turn": get_turn,
    "get_lobby": get_lobby,
}

cwd: str = getcwd()
console: Console = Console()

# Console colors
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"
TXT_INFO: str = "bold yellow"

# Self host and port
HOST: str = ""
PORT: int = 6666
LISTEN: int = 2

# Database host and port
DB_HOST: str = ""
DB_PORT: int = 8888

# Players and lobby
lobby: list = []

if __name__ == "__main__":
    # Set up TCP socket
    sock = socket()
    sock.bind((HOST, PORT))
    sock.listen()

    # Connect to the database
    try:
        db_conn = create_connection((DB_HOST, DB_PORT))
    except ConnectionRefusedError:
        console.log(f"Connection to database on {DB_HOST}:{DB_PORT} has failed.", style=TXT_DCON)

    console.print(f"Starting server on {HOST}:{PORT}.", style=TXT_DCON)

    accept(sock)

    console.print("Stopping server.")
    db_conn.close()
