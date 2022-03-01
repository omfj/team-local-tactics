from socket import create_connection
from rich.console import Console

console = Console()

sock = create_connection(("localhost", 6666))

while True:
    print("Welcome to the socket")
    command = input("Please enter a command: ")
    if command:
        sock.send(command.encode())
        response = sock.recv(1024).decode()
        if response:
            console.print(response)
    else:
        console.print("No command entered")