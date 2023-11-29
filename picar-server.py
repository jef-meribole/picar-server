from socket import *
from picarx import Picarx
from time import sleep, perf_counter

SLEEP_TIME = 0.001
CURRENT_ID = 0
LAST_COMMMAND = f"STOP:{0}"

def init_actions():
    actions = {
        "forward": move_forward,
        "backward": move_backward,
        "left": move_car,
        "right": move_car,
        "stop": stop_car
    }

    return actions


def has_new_command(current_command) -> bool:
    return current_command == LAST_COMMMAND


def move_forward():
    picar = Picarx()
    speed = 100
    while speed >= 0 and not has_new_command():
        picar.forward(speed)
        sleep(SLEEP_TIME)
        speed -= 1


def stop_car():
    picar = Picarx()
    picar.forward(0)


def move_backward():
    picar = Picarx()
    picar.forward(-1*unit)


def do_action(action: str, action_id: int) -> None:
    action = action.lower()
    actions = init_actions()
    valid_action = action in actions.keys()

    if not valid_action:
        print("INVALID ACTION SENT")
        return

    # Execute action with given unit
    actions[action](action_id)


def move_car(unit: int) -> None:
    print(f"ACTION: {unit}")


def main():
    mySock = socket(AF_INET, SOCK_DGRAM)
    mySock.bind(("", 12000))

    while True:
        command, clientAddress = mySock.recvfrom(2048)
        CURRENT_ID += 1

        command = f"{command.decode()}:{CURRENT_ID}"
        do_action(command, CURRENT_ID)
        print(command)

        mySock.sendto("got it".encode(), clientAddress)


if __name__ == "__main__":
    main()
