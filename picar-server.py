from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM
import threading
from picarx import Picarx  # pylint: disable=import-error

SLEEP_TIME = 0.01
CURRENT_ID = 0
CURRENT_ACTION = "stop"  # starting defualt commanad

LAST_RECEIVED_COMMAND_ID = 0
LAST_RUN_COMMMAND_ID = 0


def init_actions() -> dict:
    """Creates action keys and maps them to functions

    Returns:
        dict: _description_
    """
    actions = {
        "forward": move_forward,
        "backward": move_backward,
        "left": move_left,
        "right": move_right,
        "stop": stop_car,
    }

    return actions


def move_left(current_action, action_id):
    pass


def move_right(current_action, action_id):
    pass


def has_new_command(current_action, action_id) -> bool:
    running_action = make_command(current_action, action_id)
    last_received_action = make_command(CURRENT_ACTION, CURRENT_ID)
    return running_action != last_received_action


def move_motor(motor_spin: int, rate: int, action: str, action_id: int) -> None:
    picar = Picarx()
    speed = motor_spin
    move_speed = speed * rate
    picar.forward(move_speed)
    sleep(0.1)
    while speed > 0:
        speed -= 1
        picar.forward(move_speed)
        print(move_speed)
        sleep(SLEEP_TIME)

        if has_new_command(action, action_id) and speed < 50:
            return

    stop_car(action, action_id)


def move_forward(action: str, action_id: int) -> None:
    move_motor(action=action, action_id=action_id, motor_spin=100, rate=1)


def stop_car(action: str, action_id: int) -> None:
    picar = Picarx()
    picar.forward(0)


def move_backward(action: str, action_id) -> None:
    move_motor(action=action, action_id=action_id, motor_spin=100, rate=-1)


def make_command(action, action_id) -> str:
    return f"{action}:{action_id}"


def do_action(action: str, action_id: int) -> None:
    global LAST_RUN_COMMMAND_ID
    action = action.lower()
    actions = init_actions()
    valid_action = action in actions.keys()

    if not valid_action:
        print("INVALID ACTION SENT")
        return

    # Execute action with given unit
    actions[action](action, action_id)
    LAST_RUN_COMMMAND_ID = action_id


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


def run_actions():
    while True:
        current_command = CURRENT_ACTION
        current_id = CURRENT_ID

        # Don't keep repeating the same action
        if current_id != LAST_RUN_COMMMAND_ID:
            print(f"executing action: {make_command(current_command, current_id)}")
            do_action(current_command, current_id)


def main():
    server_thread = threading.Thread(target=run_server)
    action_thread = threading.Thread(target=run_actions)

    server_thread.start()
    action_thread.start()


if __name__ == "__main__":
    main()
