#!/usr/bin/env python3

from socket import socket
from threading import Thread
from rich.console import Console
from game_logic import Match, Team
import json
from os import getcwd
from os import name as os_name


def accept(sock: str) -> None:
    while True:
        conn: str; address: tuple
        conn, address = sock.accept() 
        console.log(f"Connection: '{conn}', from '{address}'")
        Thread(target=read, args=(conn, address)).start()


def read_database(database_name: str) -> str:
    try:
        with open(f"{cwd}{SLASH}database{SLASH}{database_name}.json", "r") as f:
            database_conent: str = json.dumps(json.load(f))
        f.close()
        
        return database_conent
    except Exception as e:
        console.log(f"Issues with reading the database, {database_name}.json.")
        console.log(f"Reason: {e}")
        return "error"


def start_lobby(conn: socket, address: str, port: int, name: str, champions: list=[]) -> None:
    game_lobby.append((conn, address, port, name, champions))
    console.log(f"'{name}' joined the game lobby. ({len(game_lobby)}/2)")

    if len(game_lobby) >= 2:
        for player in game_lobby:
            player[0].sendall("lobby_found".encode())
        console.log(f"Lobby full - {game_lobby}")
        start_game()


def start_game() -> None:
    console.log("Starting game...")

    for _ in range(2):
        for selecting_player in game_lobby:
            selecting_player_conn: socket = selecting_player[0]
            selecting_player_name: str = selecting_player[3]
            selecting_player_conn.sendall("choose_champion".encode())
            for waiting_player in game_lobby:
                if waiting_player != selecting_player:
                    waiting_player_conn = waiting_player[0]
                    waiting_player_conn.send("waiting".encode())
            input_champion(selecting_player_conn, selecting_player_name)

    player1_name: str = game_lobby[0][3]
    player2_name: str = game_lobby[1][3]
    player1_champions: list = game_lobby[0][4]
    player2_champions: list = game_lobby[1][4]

    console.log(f"{player1_name} - {player1_champions}")
    console.log(f"{player2_name} - {player2_champions}")
    

    match = Match(
        Team([champions[name] for name in player1]),
    )
    match.play()


def input_champion(choosing_player_conn: socket, choosing_player_name: str):
    champions = json.loads(read_database("champions"))

    while True:
        champion_selected = choosing_player_conn.recv(1024).decode().lower()
        player1_champions: list = [champion for champion in game_lobby[0][4]]
        player2_champions: list = [champion for champion in game_lobby[1][4]]
        ERROR: str = "[bold red]"

        if champion_selected not in [champion["name"] for champion in champions]:
            choosing_player_conn.sendall(f"{ERROR}Champion does not exist...".encode())
        elif champion_selected in player1_champions:
            choosing_player_conn.sendall(f"{ERROR}Champion has already been chosen...".encode())
        elif champion_selected in player2_champions:
            choosing_player_conn.sendall(f"{ERROR}Champion has already been chosen...".encode())
        else:
            choosing_player_conn.sendall(f"champion_locked_in".encode())
            for players in game_lobby:
                player_name = players[3]
                player_champions = players[4]
                if choosing_player_name == player_name:
                    for champion in champions:
                        if champion["name"] == champion_selected:
                            player_champions.append(champion_selected)
            break


def read(conn: socket, address: tuple) -> None:
    while True:
        client_input: str = conn.recv(1024)
        
        if client_input:
            client_input_decoded: str = client_input.decode()
            console.log(f"{address} asked for input: '{client_input_decoded}'")

            if client_input_decoded.split("_", 1)[0] == "get":
                match client_input_decoded:
                    case "get_help_database":
                        database_content: str = read_database("help")
                        if database_content != "error":
                            console.log(f"Sendig help database to {address}")
                            conn.sendall(database_content.encode())
                    case "get_champions_database":
                        database_content: str = read_database("champions")
                        if database_content != "error":
                            console.log(f"Sending champions database to {address}.")
                            conn.sendall(database_content.encode())
                    case "get_match_history_database":
                        database_content: str = read_database("match_history")
                        if database_content != "error":
                            console.log(f"Sending match history to {address}.")
                            conn.sendall(database_content.encode())

            elif client_input_decoded.split("_", 1)[0]== "game":
                player_name: str = client_input_decoded.split("_", 2)[2]
                method: str = client_input_decoded.split("_", 2)[1]
                player_address: str = tuple(address)[0]
                player_port: int = tuple(address)[1]

                # game_start_name
                if method == "start":
                    start_lobby(conn, player_address, player_port, player_name)
            else:
                print(f"{address} sent an unknown command: '{client_input_decoded}'")
                conn.sendall("error".encode())
        else:
            console.log(f"{address} disconnected.", style="bold red")
            conn.close()
            break


error_text: str = str(["error", "An error occurred loading the data."]).encode()
cwd: str = getcwd()
console: Console = Console()

HOST: str = "localhost"
PORT: int = 6666
LISTEN: int = 2

if os_name == "nt":
    SLASH = "\\"
else:
    SLASH = "/"

game_lobby: list[tuple[socket, str, int, str, list]] = []

if __name__ == "__main__":
    # Set up TCP socket
    sock = socket()
    sock.bind((HOST, PORT))
    sock.listen()

    console.print(f"Starting server on {HOST}:{PORT}", style="bold red")
    console.print(f"Running on {os_name.upper()}", style="bold yellow")

    accept(sock)

    console.print("Stopping server.")
    sock.close()
