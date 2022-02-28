from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from game_logic import Match, Shape, Team
import os
import sys
import json

console: object = Console()
prompt: object = Prompt()
cwd: str = os.getcwd()


# Color variables
TITLE: str = "bold blue"
T_H_CLR: str = "bold green"
T_B_CLR: str = "cyan"
TXT_CLR: str = "white"
ERR_CLR: str = "bold red"
P1_CLR: str = "bold blue"
P2_CLR: str = "bold red"
PROMPT: str = ">>>"


def welcome_message() -> None:
    # Instantiate the console
    console.print("Welcome to", style="bold", end=" ")
    console.print("Team Local Tactics!", style=TITLE)
    console.print("Type 'help' for a list of commands.", end="\n\n")


def help_message() -> None:
    console.print("Here are the commands you can use:", style="bold yellow")

    # Opens the help file and reads it
    try:
        with open(cwd + "/src/database/help.json") as f:
            commands: list = json.load(f)
            for command in commands:
                name: str; description: str; alias: str 
                name, description, alias = command["name"], command["description"], command["alias"]
                console.print(f"'{name}' - {description}" +
                              (f" (alias: '{alias}')" if alias else ""))
    except Exception as e:
        console.print(f"Error with help.json: {e}", style=ERR_CLR)
    f.close()


def get_match_history(id="0") -> None:
    # Make the table title and headers
    try:
        with open(cwd + "/src/database/match_history.json") as f:
            matches: list = json.load(f)
            match: dict = matches[int(id)]
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

    except Exception as e:
        console.print(f"Error with match_history.json: {e}", style=ERR_CLR)
    f.close()


def get_match_history_overview() -> None:
    try:
        with open(cwd + "/src/database/match_history.json") as f:
            matches: list = json.load(f)
            console.print("Match history overview", style=f"{TITLE} underline")
            print()
            for id, match in enumerate(matches):
                console.print(f"Match: {match['time']} | ID: {id}")

    except Exception as e:
        console.print(f"Error with match_history.json: {e}", style=ERR_CLR)
    f.close()


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


def clear_screen() -> None:
    if os.name == "posix":
        os.system("clear")
    elif os.name == "nt":
        os.system("cls")
    else:
        console.print("Could not clear the screen.", style=ERR_CLR)


def restart() -> None:
    console.print("Restarting...", style="green", end="\n\n")

    # Restartes program
    os.execv(sys.executable, ['python3'] + sys.argv)


def print_all_champions() -> None:
    # Make the table title and headers
    table = Table(title="🏆 Champions 🏆", header_style=T_H_CLR)
    table.add_column("Name", justify="left", style=T_B_CLR)
    table.add_column("Rock", justify="left", style=T_B_CLR)
    table.add_column("Paper", justify="left", style=T_B_CLR)
    table.add_column("Scissors", justify="left", style=T_B_CLR)

    # Open the champions file and reads it
    try:
        with open(cwd + "/src/database/champions.json") as f:
            data: list = json.load(f)
            data.sort(key=lambda x: x["name"])
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


def get_all_champions() -> None:
    # Open the champions file from the database and returns it
    try:
        with open(cwd + "/src/database/champions.json") as f:
            champions: list = json.load(f)
        f.close()
        return champions
    except Exception as e:
        console.print(f"Error with champions.json: {e}", style=ERR_CLR)


def input_champion(prompt: str, color: str, champions: list, player1: list, player2: list) -> tuple[list, list]:
    # Prompts user to input a champion
    while True:
        match Prompt.ask(f'[{color}]{prompt}').lower():
            case name if name not in champions:
                console.print(
                    f'The champion {name} is not available. Try again.', style=ERR_CLR)
            case name if name in player1:
                console.print(
                    f'{name} is already in your team. Try again.', style=ERR_CLR)
            case name if name in player2:
                console.print(
                    f'{name} is in the enemy team. Try again.', style=ERR_CLR)
            case _:
                player1.append(name)
                break

    return player1, player2



def print_summary(match: any) -> None:

    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    # For each round print a table with the results
    for index, round in enumerate(match.rounds):

        # Create a table containing the results of the round
        round_summary = Table(title=f'Round {index+1}')

        # Add columns for each team
        round_summary.add_column("Red",
                                 style="red",
                                 no_wrap=True)
        round_summary.add_column("Blue",
                                 style="blue",
                                 no_wrap=True)

        # Populate the table
        for key in round:
            red, blue = key.split(', ')
            round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                  f'{blue} {EMOJI[round[key].blue]}')
        print(round_summary)
        print('\n')

    # Print the score
    red_score, blue_score = match.score
    print(f'Red: {red_score}\n'
          f'Blue: {blue_score}')

    # Print the winner
    if red_score > blue_score:
        print('\n[red]Red victory! :grin:')
    elif red_score < blue_score:
        print('\n[blue]Blue victory! :grin:')
    else:
        print('\nDraw :expressionless:')


def start() -> None:
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("Press <Ctrl> + <C> to exit at any time during the champion selection.", style="underline")
    console.print("First we start off by choosing your champions.",
                  style=TXT_CLR, end="\n\n")

    print_all_champions()

    champions: list = get_all_champions()

    player1: list = []
    player2: list = []

    # Try clause to catch "Ctrl + C/KeyboardInterrupt"
    # So you can exit if you wrote the name or wrong or something
    try:
        player1_name: str = prompt.ask(
            f"Player 1, what is your name? (empty for Player 1)")
        if not player1_name:
            player1_name: str = "Player 1"

        player2_name: str = prompt.ask(
            f"Player 2, what is your name? (empty for Player 2)")
        if not player2_name:
            player2_name: str = "Player 1"

        # Champion selection
        for _ in range(2):
            input_champion(player1_name, P1_CLR, champions, player1, player2)
            input_champion(player2_name, P2_CLR, champions, player2, player1)

        print('\n')

        match = Match(
            Team([champions[name] for name in player1]),
            Team([champions[name] for name in player2])
        )
        match.play()

        # Print summary of match, and adds the match to match history.
        print_summary(match)
    except KeyboardInterrupt:
        console.print("\n\nExiting champion selection...", style="red", end="\n\n")


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
    "hisover": get_match_history_overview,

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
        command, arg = (command + " ").split(" ", 1)
        # Check if the command is in the commands dictionary
        if command in commands:
            if arg:
                commands[command](arg)
            else:
                commands[command]()
            print()
        elif command == ("exit" or "e"):
            console.print("Goodbye!", style="bold green")
            break
        else:
            error_command(command)
