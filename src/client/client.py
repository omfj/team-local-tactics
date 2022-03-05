#!/usr/bin/env python3

from http import server
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import track
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
    console.print("Welcome to", style="bold", end=" ")
    console.print("Team Local Tactics!", style=TITLE)
    console.print("Type 'help' for a list of commands.", end="\n\n")

# Clears the screen if the operatingsystem is unix-like. *Issues on windows
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

# Prints the match history. By default it prints an overview, but you can get all the details for a specific match by typing 'match <match_id>'
def show_match_history(id: Optional[int or str]="all") -> None:
    match_history_database: list = get_database_content("match_history")
    if id == "all":
        match_history_overview(match_history_database)
    else:
        if id.isdigit():
            id = int(id, 10)
            try:
                match_history(match_history_database, id)
            except IndexError:
                console.print(f"Match does not exist. '{id}' is an invalid ID.", style=ERR_CLR)
        else:
            console.print(f"Match does not exist. '{id}' is an invalid ID.", style=ERR_CLR)

# Display the match overview
def match_history_overview(match_history_database: list) -> None:
    console.print("Match history overview", style=f"{TITLE} underline")
    print()
    for id, match in enumerate(match_history_database):
        console.print(f"Match: {match['time']} | ID: {id}")

# Display the match 
# TODO Rewrite when refactored
def match_history(match_history_database: list, id: int):
    match: dict = match_history_database[id]
    played: str = match["time"]
    player1_name: str = match["player1"]["name"].capitalize()
    player2_name: str = match["player2"]["name"].capitalize()
    player1_score: int = match["player1"]["score"]
    player2_score: int = match["player2"]["score"]
    
    # Title
    console.print(f"{player1_name} vs {player2_name}", style=f"{TITLE} underline")
    console.print(f"Played at: {played}.")

    # Determine winner
    if player1_score > player2_score:
        console.print(f"{player1_name} won the game.")
    elif player2_score > player1_score:
        console.print(f"{player2_name} won the game.")
    else:
        console.print("It was a tie.")


    # Score of each player
    for i in range(1, 3):
        print()
        player_name: str = match[f"player{i}"]["name"].capitalize()
        player_score: int = match[f"player{i}"]["score"]
        player_champions: list = match[f"player{i}"]["champions"]
        
        console.print(player_name)
        console.print(f"\tScore: {player_score}")
        console.print("\tChampions:")
        for champion in player_champions:
            console.print(f"\t\t{champion.capitalize()}")

# TODO Kan vente med denne
# If the command is not recognized, print an error message. Also try to find what command the user meant.
def error_command(command: str) -> None:
    console.print(f"Unknown command: '{command}'.", style=ERR_CLR)

    possible_commands: list = []
    for known_command in commands:
        if command in known_command:
            possible_commands.append(f"'{known_command}'")

    if possible_commands:
        console.print("Did you mean: ", style=ERR_CLR, end="")
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
        sleep(0.2)

    # Restartes program with cool progressbar
    os.execv(sys.executable, ['python3'] + sys.argv)

# Gets all champions from the server database, and prints them in a table with their name and stats.
def print_all_champions() -> None:

    # Make the table title and headers
    table = Table(title="Champions", header_style=T_H_CLR)
    table.add_column("Name", justify="left", style=T_B_CLR)
    table.add_column("Rock", justify="left", style=T_B_CLR)
    table.add_column("Paper", justify="left", style=T_B_CLR)
    table.add_column("Scissors", justify="left", style=T_B_CLR)

    champions_database: list = get_database_content("champions")

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
    database_content: list = send_recieve(f"get_database {database_name}")
    return eval(database_content)


# TODO 3 Argument for playing against AI
# Starts the game. First asks for name, then waits until two players are connected.
def start_lobby() -> None:
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("Press <Ctrl> + <C> to exit at any time during the champion selection.", style="underline", end="\n\n")

    print_all_champions()

    player_name: str = prompt.ask("Summoner, what is your name?") 

    if player_name == "":
        player_name = f"Player {send_recieve('whoami')}"

    console.print(f"Welcome, {player_name}!")

    sock.send(f"start_lobby {player_name}".encode())

    if sock.recv(1024).decode() == "lobby_found":
        start_game()


def validate_champion(prompt: str) -> None:
    all_champions: list = get_database_content("champions")

    lobby: list = eval(send_recieve("get_lobby"))
    my_id: int = int(send_recieve("whoami"))
    other_id: int = (my_id + 1) % 2

    my_champions: list = lobby[my_id][1]
    other_champions: list = lobby[other_id][1]

    console.log(my_champions)
    console.log(other_champions)

    while True:
        name: str = Prompt.ask(f"[bold yellow]{prompt}").lower()
        match name:
            case name if name not in [champion["name"] for champion in all_champions]:
                console.print(f"The champion '{name}' is not available. Try again.", style=ERR_CLR)
            case name if name in my_champions:
                console.print(f"'{name}' is already in your team. Try again.", style=ERR_CLR)
            case name if name in other_champions:
                console.print(f"'{name}' is in the enemy team. Try again.", style=ERR_CLR)
            case _:
                for champion in all_champions:
                    if champion["name"] == name:
                        sock.sendall(f"add_champion {champion}".encode())
                break


def get_turn() -> int:
    sleep(1)
    n_picked: int = int(send_recieve("total_picked"))
    picks_left = 4 - n_picked
    player_id: int = int(send_recieve("whoami"))
    return (picks_left + (player_id)) % 2


def start_game() -> None:
    console.print("Contestant found!", style="green")
    
    pick: list[str] = ["first", "second"]
    n: int = 0

    while n < 2:
        turn: int = get_turn() 

        match turn:
            case 0:
                validate_champion(f"Pick your {pick[n]} champion")
                n += 1
            case 1:
                sleep(3)

        

def send_recieve(command: str) -> str:
    sock.sendall(command.encode())
    return sock.recv(1024).decode()

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

# What HOST and PORT the socket should connect to.
HOST: str = ""
PORT: int = 6666

# If name is main run this.
if __name__ == "__main__":
    print()

    try:
        sock: socket = create_connection((HOST, PORT))
        help_database = get_database_content("help")
        welcome_message()
    except ConnectionRefusedError:
        console.print("Could not connect to the server.", style=ERR_CLR)

    try:
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
