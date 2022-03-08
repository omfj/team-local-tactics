#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from types import NoneType
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import track
from functools import reduce
from operator import concat
from typing import Optional
from time import sleep
from socket import socket, create_connection
import os
import sys


console: object = Console()
prompt: object = Prompt()
cwd: str = os.getcwd()

# Style variables for console.print()
TITLE: str = "bold blue"
T_H_CLR: str = "bold green"
T_B_CLR: str = "cyan"
TXT_CLR: str = "white"
ERR_CLR: str = "bold red"
INF_CLR: str = "bold yellow"
P1_CLR: str = "bold blue"
P2_CLR: str = "bold red"
PROMPT: str = ">>>"

# Welcome message for the start of the game
def welcome_message() -> None:
    print()
    console.print("Welcome to", style="bold", end=" ")
    console.print("Team Local Tactics!", style=TITLE)
    console.print("Type 'help' for a list of commands.", end="\n\n")

# Clears the screen if the operatingsystem is unix-like. *Issues on windows CMD.
def clear_screen() -> None:
    if os.name == "posix":
        os.system("clear")
    else:
        console.print("Could not clear the screen.", style=ERR_CLR)

# Help message, prints all commands by default, but you can get help for a specific command by typing 'help <command>'
def help_message(command_name="all") -> None:
    if command_name == "all":
        console.print("Here are the commands you can use:", style=INF_CLR)
        for command in help_database:
            name: str; description: str; alias: str 
            name, description, alias = command["name"], command["description"], command["alias"]
            console.print(f"'{name}' - {description}" +
                            (f" (alias: '{alias}')" if alias else ""))
    elif command_name in [command["name"] for command in help_database]:
        console.print(f"How to use '{command_name}'.", style=INF_CLR)
        for command in help_database:
            if command["name"] == command_name:
                console.print(f"{command['name']} - {command['description']}" +
                             (f" (alias: '{command['alias']}')" if command["alias"] else ""))
                console.print(f"Usage: {command['usage']}")
    else:
        console.print(f"Unknown command: '{command_name}'. Remember you can't use aliases on with the help command.", style=ERR_CLR)

# Prints the match history. By default it prints an overview, but you can get 
# all the details for a specific match by typing 'match <match_id>'
def show_match_history(id: Optional[int or str]="all") -> None:
    match_history_database: list = get_database_content("match_history") #Gets the match history from the database
    try:
        if id == "all":
            match_history_overview(match_history_database)
        elif id == "last":
            match_history(match_history_database, -1)
        else:
            if id.isdigit():
                id = int(id, 10)
                try:
                    match_history(match_history_database, id)
                except IndexError: #If user enters invalid Match ID. A match that hasn't been played yet.
                    console.print(f"Match does not exist. '{id}' is an invalid ID.", style=ERR_CLR)
            else:
                console.print(f"Match does not exist. '{id}' is an invalid ID.", style=ERR_CLR)
    except KeyError:
        console.print("There are no matches in the match history.", style=ERR_CLR)

# Display the match overview
def match_history_overview(match_history_database: list) -> None:
    console.print("Match history overview", style=f"{TITLE} underline")
    print()
    for id, match in enumerate(match_history_database):
        console.print(f"Match: {match['time']} | ID: {id}")

# This function displays the match. It shows the match ID, the players who played,
# their champions, what the match results were for each round aswell as the final score.
def match_history(match_history_database: list, id: int):
    match: dict = match_history_database[id]

    # Variables from the match_history dictionary
    # Sorted into variables, easier to handle
    time: str = match["time"]
    players: list = match["players"]
    rounds: dict = match["rounds"]

    # List of each players champions
    #player1_champs: list; player2_champs: list
    #player1_champs = players[0]["champions"]
    #player2_champs = players[1]["champions"]

    # Get each players name
    player1_name: str; player2_name: str
    player1_name = players[0]["name"]
    player2_name = players[1]["name"]
        
    # Get each players score
    player1_score: str; player2_score: str
    player1_score = players[0]["score"]
    player2_score = players[1]["score"]

    console.print(' vs. '.join([f"'{player['name'].capitalize()}'" for player in players]))
    console.print(f"Played at: {time}", end="\n\n")

    # Make one table for each round. The tables includes the info about that round
    for round in rounds:
        round_table = Table(title=f"Round {round}")

        for player in players:
            round_table.add_column(player["name"].capitalize(), style=T_B_CLR)

        for desc in rounds[round]:
            player1_desc, player2_desc = desc.split(" vs ")
            round_table.add_row(player1_desc.capitalize(), player2_desc.capitalize())
            

        console.print(round_table)
        sleep(0.2)

    print()

    score_table = Table(title="Final score")
    score_table.add_column("Name")
    score_table.add_column("Score")
    score_table.add_row(player1_name, f"{player1_score}")
    score_table.add_row(player2_name, f"{player2_score}")
    console.print(score_table)

    # Determine the winner
    if player1_score < player2_score:
        console.print(f"{players[1]['name']} won the game!")
    elif player2_score < player1_score:
        console.print(f"{players[0]['name']} won the game!")
    else:
        console.print(f"It was a tie!")

# If the command is not recognized, print an error message. Also try to find what command the user meant.
def error_command(command: str) -> None:
    console.print(f"Unknown command: '{command}'.", style=ERR_CLR)

    possible_commands: list = [] # Empty list which will be appended to
    for known_command in commands: # Here, commands is the dictionary on line 320.
        if command in known_command: # Checks in command from user-input is in the dictionary.
            possible_commands.append(f"'{known_command}'") # Appends the commands from the dictionary that the user maybe meant

    if possible_commands: # Check that is not empty
        console.print("Did you mean: ", style=ERR_CLR, end="") # Prints the possible commands from the possible commands list.
        if len(possible_commands) == 1:
            console.print(possible_commands[0], end="")
        elif len(possible_commands) == 2:
            console.print(" or ".join(possible_commands), style=ERR_CLR, end="")
        else:
            console.print(", ".join(possible_commands[:-1]), end="")
            console.print(f" or {possible_commands[-1]}", style=ERR_CLR, end="")
        console.print("?", style=ERR_CLR)

    console.print("Type 'help' for a list of commands.", end="\n\n")


# Restarts the program using the python3 argument on current file. Might not work if you are using a different interpreter.
def restart() -> None:
    for _ in track(range(10), description="Restarting..."):
        sleep(0.2) #Cool progressbar to show the user that the client is restarting.

    # Restartes program.
    os.execv(sys.executable, ['python3'] + sys.argv)

# Gets all champions from the server database, and prints them in a table with their name and stats.
def print_all_champions() -> None:

    # Make the table title and headers
    table = Table(title="Champions", header_style=T_H_CLR)
    table.add_column("Name", justify="left", style=T_B_CLR)
    table.add_column("Rock", justify="left", style=T_B_CLR)
    table.add_column("Paper", justify="left", style=T_B_CLR)
    table.add_column("Scissors", justify="left", style=T_B_CLR)

    champions_database: list = get_database_content("champions") # Asks the server to fetch the champions from the
    # champions database.

    # Adds rows with the different percentages from the champion database
    for champion in champions_database:
        table.add_row(
            champion["name"].capitalize(),
            str(champion["abilities"]["rock"]) + "%",
            str(champion["abilities"]["paper"]) + "%",
            str(champion["abilities"]["scissors"]) + "%"
        )

    console.print(table)

# Sends what database the client needs, and the server returns the database
def get_database_content(database_name: str) -> str:
    # Uses the send_receive function to send a request to the server
    # Server fetches the database
    database_content: list = send_recieve(f"get_database {database_name}")
    return eval(database_content) # Returns the database content, eval evaluates the 'string' as a python expression


# Starts the game. First asks for name, then waits until two players are connected.
def start_lobby() -> None:
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("Press <Ctrl> + <C> to exit at any time during the champion selection.", style="underline", end="\n\n")
    for _ in track(range(10), description="Printing champions..."):
        sleep(0.5)
    print_all_champions()

    player_name: str = prompt.ask("Summoner, what is your name?") # Ask player for name input

    if player_name == "":
        player_name = f"Player {send_recieve('whoami')}"

    console.print(f"Welcome, {player_name}!")
    
    # Waits while a second player connects to the lobby, if send_receive function recieves 'lobby found'
    # by server, then the console.status stops and the start_game() is activated.
    # A progressbar is initiated to prepare the players for the champion selection!
    with console.status("[bold green]Searching for a challenger...", spinner="earth") as status:
        if send_recieve(f"start_lobby {player_name}") == "lobby_found":
            status.stop()
            start_game()



def validate_champion(prompt: str) -> None:
    all_champions: list = get_database_content("champions")

    my_champions: list = eval(send_recieve("filter_champs me"))
    my_champions: list = reduce(concat, my_champions)
    other_champions: list = eval(send_recieve("filter_champs other"))
    other_champions: list = reduce(concat, other_champions)

    while True:
        name: str = Prompt.ask(f"[bold yellow]{prompt}").lower()
        match name:
            case name if name not in [champion["name"] for champion in all_champions]:
                console.print(f"The champion '{name.capitalize()}' is not available. Try again.", style=ERR_CLR)
            case name if name in [champion["name"] for champion in my_champions]:
                console.print(f"'{name.capitalize()}' is already on your team. Try again.", style=ERR_CLR)
            case name if name in [champion["name"] for champion in other_champions]:
                console.print(f"'{name.capitalize()}' is in the enemy team. Try again.", style=ERR_CLR)
            case _:
                for champion in all_champions:
                    if champion["name"] == name:
                        sock.sendall(f"add_champion {champion}".encode())
                break


def get_turn() -> int:
    sleep(0.1)
    n_picked: int = int(send_recieve("total_picked"))
    picks_left = 4 - n_picked
    player_id: int = int(send_recieve("whoami"))
    return (picks_left + (player_id)) % 2


def start_game() -> None:
    console.print("Contestant found!", style="green")
    console.print(f"Playing against: {send_recieve('get_opponent_names')}", style="bold red")
    
    pick: list[str] = ["first", "second"]
    n: int = 0

    with console.status("[green]Your opponent is picking a champion...") as status:
        while n < 2:
            status.start()
            turn: int = get_turn() 
            match turn:
                case 0:
                    status.stop()
                    validate_champion(f"Pick your {pick[n]} champion")
                    n += 1
                case 1:
                    sleep(0.5)
        else:
            end_game()


def end_game() -> None:
    with console.status("[green]Your opponent is picking a champion...") as status:
        while int(send_recieve("total_picked")) < 4:
            sleep(1)
        else:
            status.stop()
            with console.status("[bold green]Playing the game...") as status:
                while sock.recv(1024).decode() != "game_end":
                        sleep(1)
                else:
                    status.stop()
                    show_match_history("last")
                    console.print("GG WP!")
        


# Function which uses a socket to send all data with the command that is given to it
# aswell as recieve the data that is sent to it.
def send_recieve(command: str) -> str:
    sock.sendall(command.encode())
    return sock.recv(8024).decode()

# All the possible commands the user can use, and their methods
commands = {
    # Start game TODO
    "start": start_lobby,
    "s": start_lobby,

    # Get help
    "help": help_message,
    "h": help_message,

    # Get match history
    "history": show_match_history,
    "his": show_match_history,

    # Get champions
    "champions": print_all_champions,
    "champs": print_all_champions,

    # Clear screen
    "clear": clear_screen,

    # Restart
    "restart": restart,
    "r": restart,
}

# If name is main run this.
if __name__ == "__main__":
    HOST: str; PORT: int

    welcome_message()

    PORT = 6666
    if "docker" in sys.argv:
        HOST = "server"
    else:
        HOST = ""

    try:
        sock: socket = create_connection((HOST, PORT)) # Creates a connection to the server
        help_database = get_database_content("help")  # The help database is fetched immediately when client is connected
    except ConnectionRefusedError: # If client could not connect to the server.
        console.print("Could not connect to the server.", style=ERR_CLR)

    try: # Splits the user input by a space to seperate the command and the argument the user gives
        # For example: help start (help is the command, start is the argument)
        while (command := input(f"{PROMPT} ")):
            command: str; arg: str
            command, arg = (command + " ").split(" ", 1)
            arg = arg.strip()

            # Check if the command is in the commands dictionary
            if command in commands:
                if arg:
                    commands[command](arg)
                else:
                    commands[command]()
                print()
            elif command in ["exit", "e"]:
                console.print("\nGoodbye!", style="bold green")
                break
            else:
                error_command(command)
    except KeyboardInterrupt or EOFError:
        console.print("\n\nGoodbye!", style="bold green")
