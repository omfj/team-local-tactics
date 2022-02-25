import json
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
import os
import sys
from game import Champion, Match, Shape, Team
from commands import help_message, get_match_history, error_command, clear_screen, restart, welcome_message
from commands import TITLE, T_H_CLR, T_B_CLR, TXT_CLR, ERR_CLR, P1_CLR, P2_CLR, PROMPT

console = Console()
prompt = Prompt()

cwd = os.getcwd()


def print_all_champions():
    # Make the table title and headers
    table = Table(title="🏆 Champions 🏆", header_style=T_H_CLR)
    table.add_column("Name", justify="left", style=T_B_CLR)
    table.add_column("Rock", justify="left", style=T_B_CLR)
    table.add_column("Paper", justify="left", style=T_B_CLR)
    table.add_column("Scissors", justify="left", style=T_B_CLR)
    
    # Open the champions file and reads it
    try:
        with open(cwd + "/src/database/champions.json") as f:
            data = json.load(f)
            for champion in data:
                table.add_row(
                    champion["name"].capitalize(), 
                    str(champion["abilities"]["rock"]) + "%",
                    str(champion["abilities"]["paper"]) + "%", 
                    str(champion["abilities"]["scissors"]) + "%"
                )
        f.close()
        console.print(table)
    except Exception as e:
        console.print(f"Error with champions.json: {e}", style=ERR_CLR)


def get_all_champions():
    with open(cwd + "/src/database/champions.json") as f:
        champions_objs = json.load(f)
        for champion in champions_objs:
            champions = [champion["name"]]
    f.close()
    return champions


def input_champion(prompt, color, champions, player1, player2):
    # Prompts user to input a champion
    while True:
        match Prompt.ask(f'[{color}]{prompt}'):
            case name if name not in champions:
                console.print(f'The champion {name} is not available. Try again.', style=ERR_CLR)
            case name if name in player1:
                console.print(f'{name} is already in your team. Try again.', style=ERR_CLR)
            case name if name in player2:
                console.print(f'{name} is in the enemy team. Try again.', style=ERR_CLR)
            case _:
                player1.append(name)
                break

    return player1, player2




def start():
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("First we start off by choosing your champions.", style=TXT_CLR, end="\n\n")

    print_all_champions()

    champions = get_all_champions()
    player1 = []
    player2 = []

    # Champion selection
    for _ in range(2):
        input_champion('Player 1', 'red', champions, player1, player2)
        input_champion('Player 2', 'blue', champions, player2, player1)

    print('\n')

    match = Match(
        Team([champions[name] for name in player1]),
        Team([champions[name] for name in player2])
    )
    match.play()

    # Print a summary
    print_match_summary(match)


commands = {
    # Start game TODO
    "start": start,
    "s": start,

    # Get help
    "help": help_message,
    "h": help_message,

    # Get match history TODO
    "his": get_match_history,
    "history": get_match_history,

    # Get champions
    "champions": print_all_champions,
    "champs": print_all_champions,

    # Clear screen
    "clear": clear_screen,
    
    # Restart
    "restart": restart,
}

if __name__ == "__main__":
    welcome_message()
    while (command := input(f"{PROMPT} ").lower()):
        # Print for empty space
        print()
        
        # Check if the command is in the commands dictionary
        if command in commands:
            commands[command]()
        elif command == ("exit" or "e"):
            console.print("Goodbye!", style="bold green")
            break
        else:
            error_command(command)