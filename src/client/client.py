#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    elif id == "last":
        match_history(match_history_database, -1)
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
    players: list = match["players"]
    score: list = match["score"]
    players_score: list = list(zip(players, score)) # Format ([name, score], ...)
    rounds: dict = match["rounds"]


    console.print(f"Match ID {id}")
    console.print(' vs. '.join([f"'{player.capitalize()}'" for player in players]))
    console.print(f"Played at: {played}", end="\n\n")



    round_table = Table(title="The Match", header_style=T_H_CLR)
    for round in rounds:
        console.print(f"Round {round}", justify="left", style=T_B_CLR)
        for team, champs in rounds[round].items():
            console.print(f"{team.capitalize()} - {champs.capitalize()}")
    console.print(round_table)
    print()
    
    player_scores = Table(title="Final Score", header_style=INF_CLR)
    for player_stats in players_score:
        player_scores.add_column(f"{player_stats[0]}: {player_stats[1]}")
    console.print(player_scores)
    print()

    # Print out the rounds
    #for round in rounds:
        #console.print(f"Round {round}")
        #for team, champs in rounds[round].items():
            #console.print(f"{team} - {champs}")

    #print()
    # Determine the winner
    if players_score[0][1] == 6:
        console.print(f"Winner: {players_score[0][0].capitalize()}! GG EZ")
    elif players_score[1][1] == 6:
        console.print(f"Winner: {players_score[1][0].capitalize()}! GG EZ")
    elif players_score[0][1] > players_score[1][1]:
        console.print(f"Winner: {players_score[0][0].capitalize()}! GG WP")
    elif players_score[1][1] > players_score[0][1]:
        console.print(f"Winner: {players_score[1][0].capitalize()}! GG WP")
    else:
        console.print(f"It was a tie! GG WP")

    

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
    for _ in track(range(10), description="Printing champions..."):
        sleep(0.5)
    print_all_champions()

    player_name: str = prompt.ask("Summoner, what is your name?") 

    if player_name == "":
        player_name = f"Player {send_recieve('whoami')}"

    console.print(f"Welcome, {player_name}!")
    
    with console.status("[bold green]Searching for a challenger...", spinner="earth") as status:
        if send_recieve(f"start_lobby {player_name}") == "lobby_found":
            status.stop()
            for _ in track(range(10), description="Starting game..."):
                sleep(0.5)
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

# What HOST and PORT the socket should connect to.
HOST: str = "" # Uncomment to run when not in docker
#HOST: str = "server" # Comment this if you uncomment the above
PORT: int = 6666

# If name is main run this.
if __name__ == "__main__":
    welcome_message()

    try:
        sock: socket = create_connection((HOST, PORT))
        help_database = get_database_content("help")
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
