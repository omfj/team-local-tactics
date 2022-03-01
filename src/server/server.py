from pydoc import cli
from socket import create_server
from threading import Thread
from rich.console import Console
from server.main import *

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


def accept(sock):
    while True:
        conn, address = sock.accept() 
        console.print(f"Connection: '{conn}', from '{address}'")
        Thread(target=read, args=(conn,)).start()


def read(conn):
    client_input = conn.recv(1024)
    client_input = client_input.decode()
    print(f"Client input: '{client_input}'")

    if client_input:
        resp = commands[client_input]()
        resp.encode()
        return resp
    else:
        console.print("Connection closed")
        conn.close()


if __name__ == "__main__":
    # Set up TCP socket
    sock = create_server(("localhost", 6666))

    # TODO Only accept 2 connections
    sock.listen(2)

    accept(sock)
