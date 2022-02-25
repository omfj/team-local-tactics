import json
from rich.table import Table
from rich.console import Console
import os

console = Console()
cwd = os.getcwd()

def welcome_message():
    # Instantiate the console
    console.print("Welcome to", style="bold", end =" ")
    console.print("Team Local Tactics!", style="bold blue")
    console.print("Type 'help' for a list of commands.")

def help_message():
    console.print("Here are the commands you can use:", style="bold yellow")
    console.print("'help' - Displays this message")
    console.print("'champions' - Displays all champions")
    console.print("'exit' - Exits the program")


def get_champions():
    # Make the table title and headers
    table = Table(title="🏆 Champions 🏆", header_style="bold green")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Rock", justify="left", style="cyan")
    table.add_column("Paper", justify="left", style="cyan")
    table.add_column("Scissors", justify="left", style="cyan")
    
    # Open the json file and read it
    with open(cwd + '/database/champions.json') as f:
        data = json.load(f)
        for champion in data:
            table.add_row(
                champion["name"].capitalize(), 
                str(champion["abilities"]["rock"]),
                str(champion["abilities"]["paper"]), 
                str(champion["abilities"]["scissors"])
            )
    f.close()
    console.print(table)

def get_match_history():
    # Make the table title and headers
    table = Table(title="📚 Match History 📚", header_style="bold green")
    table.add_column("Player 1", justify="left", style="cyan")
    table.add_column("Player 2", justify="left", style="cyan")
    table.add_column("Played", justify="left", style="red")

commands = {
    "help": help_message,
    "champions": get_champions,
}

if __name__ == "__main__":
    welcome_message()
    while (command := input(">>> ").lower()):
        if command in commands:
            commands[command]()
        elif command == "exit":
            console.print("Goodbye!", style="bold green")
            break
        else:
            console.print(f"The command '{command}' was not found. Type 'help' for a list of commands.", style="bold red")
