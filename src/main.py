import json
import yaml
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from rich.style import Style
import os
import sys

console = Console()
prompt = Prompt()
cwd = os.getcwd()

# Load settings
with open(cwd + "/src/settings.yaml") as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)
try:
    TITLE = settings["colors"]["title"]
    T_H_CLR = settings["colors"]["table"]["header"]
    T_B_CLR = settings["colors"]["table"]["body"]
    TXT_CLR = settings["colors"]["text"]
    ERR_CLR = settings["colors"]["error"]
    P1_CLR = settings["colors"]["players"][1]
    P2_CLR = settings["colors"]["players"][2]
    PROMPT = settings["gui"]["prompt"]
except:
    console.print("Could not load settings.yaml.", style="bold red")
    TITLE = "bold blue"
    T_H_CLR = "bold green"
    T_B_CLR = "cyan"
    TXT_CLR = "white"
    ERR_CLR = "bold red"
    P1_CLR = "bold blue"
    P2_CLR = "bold red"
    PROMPT = ">>>"
finally:
    settings_file.close()


def welcome_message():
    # Instantiate the console
    console.print("Welcome to", style="bold", end=" ")
    console.print("Team Local Tactics!", style=TITLE)
    console.print("Type 'help' for a list of commands.", end="\n\n")

    # Warn about root directory
    console.print("! Make sure that you run this program with", style="red", end=" ")
    console.print("team-local-tactics", style="bold red underline", end="")
    console.print(" as the root directory !", style="red")
    

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


def get_champions():
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


def get_match_history():
    # Make the table title and headers
    table = Table(title="📚 Match History 📚", header_style=T_H_CLR)
    table.add_column("Player 1", justify="left", style=T_B_CLR)
    table.add_column("Player 2", justify="left", style=T_B_CLR)
    table.add_column("Played", justify="left", style=T_B_CLR)


class Error:
    def command(command):
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


def start():
    pass


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
    "champions": get_champions,
    "champs": get_champions,

    # Clear screen
    "clear": clear_screen,
    
    # Restart
    "restart": restart,
}

if __name__ == "__main__":
    welcome_message()
    while (command := input(f"{PROMPT} ").lower()) != "e":
        # Print for empty space
        print()
        
        # Check if the command is in the commands dictionary
        if command in commands:
            commands[command]()
        elif command == "exit" or "e":
            console.print("Goodbye!", style="bold green")
            break
        else:
            Error.command(command)
