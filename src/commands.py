from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
import os
import sys

console = Console()
prompt = Prompt()

# Color variables
TITLE = "bold blue"
T_H_CLR = "bold green"
T_B_CLR = "cyan"
TXT_CLR = "white"
ERR_CLR = "bold red"
P1_CLR = "bold blue"
P2_CLR = "bold red"
PROMPT = ">>>"


def welcome_message():
    # Instantiate the console
    console.print("Welcome to", style="bold", end=" ")
    console.print("Team Local Tactics!", style=TITLE)
    console.print("Type 'help' for a list of commands.", end="\n\n")


def help_message():
    console.print("Here are the commands you can use:", style="bold yellow")
    
    # Opens the help file and reads it
    try:
        with open(cwd + "/src/database/help.json") as f:
            commands = json.load(f)
            for command in commands:
                name, description, alias = command["name"], command["description"], command["alias"]
                console.print(f"'{name}' - {description}" + (f" (alias: {alias})" if alias else ""))
    except Exception as e:
        console.print(f"Error with help.json: {e}", style=ERR_CLR)
    f.close()


def get_match_history():
    # Make the table title and headers
    table = Table(title="📚 Match History 📚", header_style=T_H_CLR)
    table.add_column("Player 1", justify="left", style=T_B_CLR)
    table.add_column("Player 2", justify="left", style=T_B_CLR)
    table.add_column("Played", justify="left", style=T_B_CLR)


def error_command(command):
    console.print(f"Unknown command: '{command}'.", style=ERR_CLR)

    possible_commands = []
    for known_command in commands:
        if command in known_command:
            possible_commands.append(f"'{known_command}'")

    if possible_commands:
        console.print("Did you mean: ", style=ERR_CLR, end="")
        console.print(", ".join(possible_commands), end="")
        console.print("?", style=ERR_CLR)
        
    console.print("Type 'help' for a list of commands.")
        

def clear_screen():
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")
    else:
        console.print("Could not clear the screen.", style=ERR_CLR)


def restart():
    console.print("Restarting...", style="green", end="\n")
    
    # Restartes program
    os.execv(sys.executable, ['python3'] + sys.argv)
