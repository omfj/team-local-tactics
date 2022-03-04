#!/usr/bin/env python3

from socket import socket, create_connection
from threading import Thread
from rich.console import Console
from game_logic import Match, Team
from os import getcwd


##### DATABASE LOGIC
# Reading the data base
def get_database(conn: socket, database_name: str) -> str:
    db_conn.sendall(f"read_database {database_name}".encode())
    db_response: str = db_conn.recv(8024).decode()
    conn.sendall(db_response.encode())


##### PLAYING TEAM LOCAL TACTICS
# A lobby, when a client is waiting for a game
def start_lobby(conn: socket, name: str) -> None:
    lobby.append((conn, name, []))
    console.log(f"'{name}' joined the game lobby. ({len(lobby)}/2)")

    if len(lobby) >= 2:
        for player in lobby:
            player[0].sendall("lobby_found".encode())
        console.log(f"Lobby full - {[player[1] for player in lobby]}")
        start_game()


# When there is a full lobby, this starts the game
def start_game() -> None:
    console.log("Starting game...")

    for _ in range(2):
        for curr_player in lobby:
            curr_player_conn = curr_player[0]
            curr_player_conn.sendall("choose_champion".encode())

            # For all the other players in the lobby
            for waiting_player in lobby:
                if not waiting_player == curr_player:
                    waiting_player_conn = waiting_player[0]
                    waiting_player_conn.sendall("waiting".encode())
    

    # match = Match(
    #     Team([player1_champions[name] for name in player1_name]), Team([player2_champions[name] for name in player2_name]))
    # match.play()

    for player in lobby:
        player[0].sendall("match_done".encode())

    console.log("Match done!", style="bold green")

# Validate a champion. If the champions passes the tests, add the champion to the players champion pool.
def validate_champion(curr_player: socket, champion_selected: str):
    champions = get_database("champions")
    ERROR: str = "[bold red]"

    player1_champions = lobby[0][2]
    player2_champions = lobby[1][2]

    if champion_selected not in [champion["name"] for champion in champions]:
        curr_player.sendall(f"{ERROR}Champion does not exist...".encode())
    elif champion_selected in player1_champions:
        curr_player.sendall(f"{ERROR}Champion has already been chosen...".encode())
    elif champion_selected in player2_champions:
        curr_player.sendall(f"{ERROR}Champion has already been chosen...".encode())
    else:
        curr_player[2].append(champions[champion_selected])
        curr_player.sendall(f"[bold green]Champion {champion_selected.capitalize()} has been added to your team!".encode())


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
        console.log(client_input)
        
        if client_input:
            client_input_decoded: str = client_input.decode().split(" ", 1)
            command: str = client_input_decoded[0]
            args: str = client_input_decoded[1]

            console.log(f"{address} sent: {client_input_decoded}")

            if command in commands:
                if args:
                    commands[command](conn, args)
                else:
                    commands[command]()
            else:
                conn.sendall("[bold red]Invalid input!".encode())

        else:
            console.log(f"Client {address} has connected", style=TXT_DCON)
            conn.close()
            break


##### MAIN #####

commands: dict = {
    "get_database": get_database,
    "validate_champion": validate_champion,
    "start_lobby": start_lobby,
}

error_text: str = str(["error", "An error occurred loading the data."]).encode()
cwd: str = getcwd()
console: Console = Console()

# Console colors
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"

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
