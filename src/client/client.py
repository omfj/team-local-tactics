from socket import create_connection
from rich.console import Console
from server import start, help_message, get_match_history, print_all_champions, clear_screen, restart

console = Console()
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
    sock = create_connection(("localhost", 6666))
    
    while True:
        print("Welcome to the socket")
        print(f"Available commands: ")
        for command in commands.keys():
            if len(command) > 3:
                print(command)
        command = input("Please enter a command: ")
        if command:
            sock.send(command.encode())
            response = sock.recv(1024).decode()
            if response:
                console.print(response)
        else:
            console.print("No command entered")