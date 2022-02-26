from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from game import Champion, Match, Shape, Team
from commands import help_message, get_match_history, error_command, clear_screen, restart, welcome_message
from commands import TITLE, T_H_CLR, T_B_CLR, TXT_CLR, ERR_CLR, P1_CLR, P2_CLR, PROMPT
import os
import json

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


def get_all_champions():
    try: 
        with open(cwd + "/src/database/champions.json") as f:
            champions = json.load(f)
        f.close()
        return champions
    except Exception as e:
        console.print(f"Error with champions.json: {e}", style=ERR_CLR)


def input_champion(prompt, color, champions, player1, player2):
    # Prompts user to input a champion
    while True:
        match Prompt.ask(f'[{color}]{prompt}').lower():
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


def print_summary(match):

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


def start():
    console.print("Welcome players, to Team Local Tactics!", style=TITLE)
    console.print("First we start off by choosing your champions.", style=TXT_CLR, end="\n\n")

    print_all_champions()

    champions = get_all_champions()

    player1 = []
    player2 = []

    player1_name = prompt.ask(f"Player 1, what is your name? (empty for Player 1)")
    if not player1_name:
        player1_name = "Player 1"

    player2_name = prompt.ask(f"Player 2, what is your name? (empty for Player 2)")
    if not player2_name:
        player2_name = "Player 1"

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