from socket import *


def init_actions():
    actions = {
        "forward": move_car,
        "backward": move_car,
        "left": move_car,
        "right": move_car,
    }

    return actions


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

    if len(action_args) != 2:
        print("malformed action")
        return

    action = action_args[0]
    unit = action_args[1]

    do_action(action, unit)
    return


def main():
    mySock = socket(AF_INET, SOCK_DGRAM)
    mySock.bind(("", 12000))

    while True:
        message, clientAddress = mySock.recvfrom(2048)
        message = message.decode()
        attempt_command(message)
        mySock.sendto("got it".encode(), clientAddress)


if __name__ == "__main__":
    main()
