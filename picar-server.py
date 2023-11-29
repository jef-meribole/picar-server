from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM
import threading
from picarx import Picarx  # pylint: disable=import-error

SLEEP_TIME = 0.001
CURRENT_ID = 0
CURRENT_ACTION = "stop"  # starting defualt commanad


def init_actions():
    actions = {
        "forward": move_forward,
        "backward": move_backward,
        "left": move_car,
        "right": move_car,
        "stop": stop_car,
    }

    return actions


def has_new_command(current_action, action_id) -> bool:
    running_action = make_command(current_action, action_id)
    last_received_action = make_command(CURRENT_ACTION, CURRENT_ID)
    return running_action != last_received_action


def move_forward(action: str, action_id: int):
    picar = Picarx()
    speed = 100
    while speed >= 0:
        if has_new_command(action, action_id):
            return

        picar.forward(speed)
        sleep(SLEEP_TIME)
        speed -= 1
        print(speed)


def stop_car(action: str, action_id: int):
    picar = Picarx()
    picar.forward(0)


def move_backward(action: str, action_id):
    picar = Picarx()
    speed = 100
    while speed >= 0:
        picar.forward(-1 * speed)

        if has_new_command(action, action_id):
            return

        sleep(SLEEP_TIME)
        speed -= 1


def make_command(action, action_id):
    return f"{action}:{action_id}"


def do_action(action: str, action_id: int) -> None:
    action = action.lower()
    actions = init_actions()
    valid_action = action in actions.keys()

    if not valid_action:
        print("INVALID ACTION SENT")
        return

    # Execute action with given unit
    actions[action](action, action_id)


def move_car(unit: int) -> None:
    print(f"ACTION: {unit}")


def run_server():
    mySock = socket(AF_INET, SOCK_DGRAM)
    mySock.bind(("", 12000))
    global CURRENT_ID
    global CURRENT_ACTION

    while True:
        command, _ = mySock.recvfrom(2048)
        command = command.decode()
        CURRENT_ID += 1
        CURRENT_ACTION = command

        print(f"Command Received: {make_command(command, CURRENT_ID)}")
        # mySock.sendto("got it".encode(), clientAddress)


def run_actions():
    while True:
        current_command = CURRENT_ACTION
        current_id = CURRENT_ID
        print(f"executing action: {make_command(current_command, current_id)}")
        do_action(current_command, current_id)


def main():
    server_thread = threading.Thread(target=run_server)
    action_thread = threading.Thread(target=run_actions)

    server_thread.start()
    action_thread.start()


if __name__ == "__main__":
    main()
