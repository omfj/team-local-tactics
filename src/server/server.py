#!/usr/bin/env python3

from socket import socket, create_connection
import sys
from game_logic import Champion, Match, Team, Shape
from datetime import datetime
from threading import Thread
from rich.console import Console
from time import sleep
from os import getcwd


##### DATABASE LOGIC
# Reading the data base
# The function retrieves command from client about which database it must fetch from the database.
# Client input is then used by server to send request to server to get the particular database
def get_database(conn: socket, database_name: str, reciver="client") -> None:
    db_conn.sendall(f"read_database {database_name}".encode())
    db_response: str = db_conn.recv(8024).decode()
    if reciver == "client":
        conn.sendall(db_response.encode())
    else:
        return eval(db_response)

#def get_database_server(database_name: str) -> list:
    #db_conn.sendall(f"read_database {database_name}".encode())
    #db_response: str = db_conn.recv(8024).decode()
    #return eval(db_response)


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

    while len(lobby) < 2: # if not 2 people in the lobby, wait for new connection.
        sleep(1)
    else: # else, lobby_found is sent to the client connection, which initiates the game.
        conn.sendall("lobby_found".encode())
        console.log(f"Lobby full - {[player[1] for player in lobby]}")

# Function which starts the game on the server side.
def play_game() -> None:

    while total_picked_server() < 4: # Waits until 4 champions have been picked before Match is initiated.
        sleep(3)
    else:
        match: Match = Match(
            Team([parse_champion(champion) for champion in lobby[0][2]]), # Adds champions to red team and blue team
            Team([parse_champion(champion) for champion in lobby[1][2]]) # respectively in variable 'match'.
        )
        match.play() # Starts the match using the game logic from game_logic.py
        send_match_summary(match, [player[1:] for player in lobby])

        for player in lobby:
            sleep(0.2) # Or else database and server get overwhelmed
            player[0].send("game_end".encode())

        console.log("Match is over!")
        lobby.clear()
        if len(lobby) == 0:
            console.log("Lobby is empty.")
        
        play_game()


# Sends match results to the database so the database can append the information to the match_history database
# The winner, the score, the time of the match and which champions played is all sent to the database by the server.
def send_match_summary(match: Match, players: list) -> None:

    match_summary: dict = {} # Dictionary to store all the information from the match
    # Dict keys are 'time', 'players', 'rounds',

    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    now = datetime.now()
    date_time = now.strftime("%d/%m %H:%M")

    match_summary["time"] = date_time

    match_summary["players"] = []
    for index, player in enumerate(players):
        name = player[0]
        champions = player[1]
        match_summary["players"].append({"name": name, "champions": [champion["name"] for champion in champions], "score": match.score[index]})
        # Adds the champion names and the score to both of the players in the list
    match_summary["rounds"] = {}
    for index, round in enumerate(match.rounds):
        n_round = index + 1
        match_summary["rounds"][f"{n_round}"] = []

        for fight in round:
            p1_champ, p2_champ = fight.split(', ')
            current_fight: list = match_summary["rounds"][f"{n_round}"]
            current_fight.append(f"{p1_champ} {EMOJI[round[fight].red]} vs {p2_champ} {EMOJI[round[fight].blue]}")

    console.log(f"Sending to database: append_database match_history {match_summary}")
    db_conn.sendall(f"append_database match_history {match_summary}".encode()) #Sends information about the match to the database

# Function which changes the format of the champion parameter and its attributes (name, rock, paper, scissors)
# so that the Champion Class in game_logic.py can understand.
def parse_champion(champion: dict) -> Champion:
    name: str; rock: int; paper: int; scissors: int

    console.log(champion)

    name = champion["name"]
    rock = champion["abilities"]["rock"] / 100
    paper = champion["abilities"]["paper"] / 100
    scissors = champion["abilities"]["scissors"] / 100

    return Champion(name, rock, paper, scissors)

# Adds champion to the roster for each player
def add_champion(conn: socket, champion: str) -> None:
    for player in lobby:
        if player[0] == conn:
            player[2].append(eval(champion))
            console.log(f"{player[1]} has: {player[2]}")

# Function which counts how many players are in the lobby
# and sends it to the client connection.
def total_picked(conn: socket) -> None:
    n: int = 0
    for player in lobby:
        n += len(player[2])
    conn.send(f"{n}".encode())

# A function where the server counts how many players are in the lobby
# returns the amount of players
def total_picked_server() -> int:
    n: int = 0
    for player in lobby:
        n += len(player[2])

    return n

# Gets the name of the player opponent for player 1.
def get_opponent_names(conn: socket) -> None:
    opponents = []
    for player in lobby:
        if player[0] != conn: # Check that both players is not from the same connection.
            opponents.append(player[1]) # Player name is added to the list

    conn.send(f"{', '.join(opponents)}".encode()) #Joins the list and sends it to the client connection.


def filter_champs(conn: socket, filter: str) -> None:
    my_champions = [] # To handle player 1 champions
    other_champions = [] # To handle player 2 champions

    for player in lobby:
        if player[0] == conn: # If player 1 has connected
            my_champions.append(player[2])
        else:
            other_champions.append(player[2]) # if player 2 has connected

    if filter == "me":
        conn.send(f"{my_champions}".encode())   
    elif filter == "other":
        conn.send(f"{other_champions}".encode())

# This function receives a connection from the client and gives the client information about which player it is
# or which player it is going to be.
def whoami(conn: socket):
    found: bool = False # Default value is False.
    for id, player in enumerate(lobby):
        if conn == player[0]: # If the connection connecting to the server is player 1
            conn.send(f"{id}".encode()) # Then send the id number to the client
            found = True # and set found equal to True
    
    if not found: # If found is True (there is a player in the lobby) then send the length of the lobby + 1.
        conn.sendall(f"{len(lobby) + 1}".encode())

# Gives the server information over how many champion picks that are left and sends it to the client.
def get_turn(conn: socket):
    picks_left = 4 - (len(lobby[0][2]) + len(lobby[1][2]))

    console.log(f"Picks left: {picks_left}", style=TXT_INFO)

    console.log(f"{picks_left % 2}", style=TXT_INFO)
    conn.send(f"{picks_left % 2}".encode())


# A function which simply removes a player from the lobby list.
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
# Commands the server recognises. Stored in a dictionary
commands: dict = {
    "get_database": get_database,
    "start_lobby": start_lobby,
    "add_champion": add_champion,
    "total_picked": total_picked,
    "whoami": whoami,
    "get_turn": get_turn,
    "filter_champs": filter_champs,
    "get_opponent_names": get_opponent_names,
}

cwd: str = getcwd()
console: Console = Console()

# Console colors
TXT_CONN: str = "bold green"
TXT_DCON: str = "bold red"
TXT_INFO: str = "bold yellow"

# Players and lobby
lobby: list = []

if __name__ == "__main__":
    HOST: str; PORT: int; DB_HOST: str; DB_PORT: int
    PORT = 6666
    DB_PORT = 8888
    if "docker" in sys.argv:
        HOST = "server"
        DB_HOST = "database"
    else:
        HOST = "localhost"
        DB_HOST = "localhost"

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

    Thread(target=play_game).start()
    accept(sock)

    console.print("Stopping server.")
    db_conn.close()
