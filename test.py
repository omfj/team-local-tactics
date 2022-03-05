from rich.console import Console

console = Console()

lobby = [["filler", "filler", []], ["filler", "filler", []]]

def get_turn():
    picks_left = 4 - (len(lobby[0][2]) + len(lobby[1][2]))

    console.log(f"Picked champions {picks_left}", style="bold yellow")

    console.log(f"{picks_left % 2}", style="bold yellow")

if __name__ == "__main__":
    n = 4
    while n > 0:
        a = input("Skriv noe: ")
        lobby[n % 2][2].append(a)
        get_turn()
        n -= 1
        for player in lobby:
            console.log(player[2])
