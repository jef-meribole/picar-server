from socket import *
from picarx import Picarx
from time import sleep

def init_actions():
    actions = {
        "forward": move_forward,
        "backward": move_backward,
        "left": move_car,
        "right": move_car,
    }

    return actions

def move_forward(unit: int):
    picar = Picarx()
    picar.forward(unit)

def stop_car():
    move_forward(0)

def move_backward(unit: int):
    picar = Picarx()
    picar.forward(-1*unit)

def do_action(action, unit) -> None:
    action = action.lower()
    actions = init_actions()
    valid_action = action in actions.keys()

    if not valid_action:
        print("INVALID ACTION SENT")
        return

    # Execute action with given unit
    actions[action](unit)


def move_car(unit: int) -> None:
    print(f"ACTION: {unit}")


def attempt_command(client_command: str) -> None:
    action_args = client_command.split(":")

    # Check if we have the correct number of arguments
    if len(action_args) != 2:
        print("malformed action")
        return

    action = action_args[0]
    unit = int(action_args[1])

    do_action(action, unit)
    return


def main():
    mySock = socket(AF_INET, SOCK_DGRAM)
    mySock.bind(("", 12000))

    while True:
        socket.settimeout(1)
        command, clientAddress = mySock.recvfrom(2048)
        if not mySock:
            stop_car()
            print("timeout")
        command = command.decode()
        attempt_command(command)
        print(command)

        mySock.sendto("got it".encode(), clientAddress)

if __name__ == "__main__":
    main()
