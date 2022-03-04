#!/usr/bin/env python3

from socket import socket, create_connection
from threading import Thread
from rich.console import Console
from game_logic import Match, Team
from os import getcwd


##### DATABASE LOGIC
# Reading the data base
def read_database(database_name: str) -> str:
    db_conn.sendall(f"read_database {database_name}".encode())
    db_response = db_conn.recv(8024).decode()
    return db_response


##### PLAYING TEAM LOCAL TACTICS
# A lobby, when a client is waiting for a game
def start_lobby(conn: socket, address: str, port: int, name: str, champions: list=[]) -> None:
    game_lobby.append((conn, address, port, name, champions))
    console.log(f"'{name}' joined the game lobby. ({len(game_lobby)}/2)")

    if len(game_lobby) >= 2:
        for player in game_lobby:
            player[0].sendall("lobby_found".encode())
        console.log(f"Lobby full - {game_lobby}")
        start_game()


# When there is a full lobby, this starts the game
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
        Team([player1_champions[name] for name in player1_name]), Team([player2_champions[name] for name in player2_name]))
    match.play()

# Input champions
def input_champion(choosing_player_conn: socket, choosing_player_name: str):
    champions = read_database("champions")

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
            console.log(f"Client {address} has connected", style=TXT_DCON)
            conn.close()
            break


##### MAIN #####
error_text: str = str(["error", "An error occurred loading the data."]).encode()
cwd: str = getcwd()
console: Console = Console()

# Console colors
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"

# Self host and port
HOST: str = "localhost"
PORT: int = 6666
LISTEN: int = 2

# Database host and port
DB_HOST: str = "localhost"
DB_PORT: int = 8888


game_lobby: list[tuple[socket, str, int, str, list]] = []

if __name__ == "__main__":
    # Set up TCP socket
    sock = socket()
    sock.bind((HOST, PORT))
    sock.listen()

    # Connect to the database
    db_conn = create_connection((DB_HOST, DB_PORT))

    console.print(f"Starting server on {HOST}:{PORT}", style="bold red")

    accept(sock)

    console.print("Stopping server.")
    db_conn.close()
