from socket import create_connection
from rich.console import Console


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