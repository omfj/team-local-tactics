#!/usr/bin/env python3

from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from time import sleep
from socket import socket
import os
import sys
import json

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
        console.print("Unknown command: '{command_name}'. Remember you can't use aliases on with the help command.", style=ERR_CLR)

# Prints the match history. By default it prints an overview, but you can get all the details for a specific match by typing 'match <match_id>'
def get_match_history(id: str = "all") -> None:
    match_history_database: list = json.loads(get_database_content("match_history"))
    if id == "all":
        get_match_history_overview(match_history_database)
    else:
        id: int = int(id)
        if id <= len(match_history_database) and id >= 0:
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
        else:
            console.print("Invalid ID.", style=ERR_CLR)

# Helper function for get_match_history()
def get_match_history_overview(match_history_database: list) -> None:
    console.print("Match history overview", style=f"{TITLE} underline")
    print()
    for id, match in enumerate(match_history_database):
        console.print(f"Match: {match['time']} | ID: {id}")

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

# Clears the screen. Checks if the user is on Windows or Linux and uses the appropriate command.
def clear_screen() -> None:
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")
    else:
        console.print("Could not clear the screen.", style=ERR_CLR)

# Restarts the program using the python3 argument on current file. Might not work if you are using a different interpreter.
def restart() -> None:
    console.print("\nRestarting...", style="green", end="\n\n")

    # Restartes program
    os.execv(sys.executable, ['python3'] + sys.argv)

# Gets all champions from the server database, and prints them in a table with their name and stats.
def print_all_champions() -> None:

    # Make the table title and headers
    table = Table(title="🏆 Champions 🏆", header_style=T_H_CLR)
    table.add_column("Name", justify="left", style=T_B_CLR)
    table.add_column("Rock", justify="left", style=T_B_CLR)
    table.add_column("Paper", justify="left", style=T_B_CLR)
    table.add_column("Scissors", justify="left", style=T_B_CLR)

    champions_database: list = json.loads(get_database_content("champions"))

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
    sock.send(f"get_{database_name}_database".encode())
    database_content: str = sock.recv(1024).decode()
    if database_content == "error":
        return f"error;Failed to load the database for: {database_name.replace('_', ' ')}."
    else:
        return database_content

# TODO 2
# TODO 3 Argument for playing against AI
# Starts the game. First asks for name, then waits until two players are connected.
def start_lobby() -> None:
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("Press <Ctrl> + <C> to exit at any time during the champion selection.", style="underline", end="\n\n")

    print_all_champions()

    player_name: str = prompt.ask("Summoner, what is your name?")
    sock.send(f"game_start_{player_name}".encode())

    try:
        with console.status("[bold green]Searching for contestant...") as status:
            while True:
                sleep(1)
                if sock.recv(1024).decode() == "lobby_found":
                    break
                else:
                    status.update(sock.recv(1024).decode())
        status.stop()
        console.print("Contestant found!", style="green")
        start_game()
    except KeyboardInterrupt:
        console.print("\nExited champion select.", style="red")
        sock.send(f"game_leave_{player_name}".encode())


def start_game() -> None:
    what_pick: list[str] = ["first", "second"]
    n_pick_champion: int = 0
    while True:
        if sock.recv(1024).decode() == "choose_champion":
            while True:
                picked_champion: str = prompt.ask(f"Choose your {what_pick[n_pick_champion]} champion")
                sock.sendall(picked_champion.encode())
                champion_pick_response = sock.recv(1024).decode()
                if champion_pick_response == "champion_locked_in":
                    console.print(f"Success, {picked_champion} is on your team!")
                    break
                else:
                    console.print(champion_pick_response)
                    continue
        elif sock.recv(1024).decode() == "waiting":
            console.print("Waiting for the other player to pick.")


# All the possible commands the user can use, and their methods
commands = {
    # Start game TODO
    "start": start_lobby,
    "s": start_lobby,

    # Get help
    "help": help_message,
    "h": help_message,

    # Get match history
    "history": get_match_history,
    "his": get_match_history,

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
HOST: str = "localhost"
PORT: int = 6666

# If name is main run this.
if __name__ == "__main__":
    sock = socket()
    sock.connect((HOST, PORT))

    help_database = json.loads(get_database_content("help"))

    # TODO method for checking the databases

    welcome_message()

    try:
        while (command := input(f"{PROMPT} ")):
            command: str; arg: str
            command, arg = (command + " ").split(" ", 1)
            # Check if the command is in the commands dictionary
            if command in commands:
                if arg:
                    commands[command](arg.strip())
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
