from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM
import threading
from picarx import Picarx  # pylint: disable=import-error

SLEEP_TIME = 0.01
CURRENT_ID = 0
CURRENT_ACTION = "stop"  # starting defualt commanad

LAST_RECEIVED_COMMAND_ID = 0
LAST_RUN_COMMMAND_ID = 0

MAX_SERVO_ANGLE = 35
SERVO_ANGLE = 0


def init_actions() -> dict:
    """Creates action keys and maps them to functions

    Returns:
        dict: Dictionary of functions & actions that can
        be accessed to run the appropriate function for a
        given action
    """
    actions = {
        "forward": move_forward,
        "backward": move_backward,
        "left": turn_left,
        "right": turn_right,
        "stop": stop_car,
    }

    return actions


def set_turn_angle(action: str, action_id: int, target_angle: int):
    """Smoothly turns from the current angle to the target angle. The current
    angle is tracked by the global variable SERVO_ANGLE

    Args:
        action (str): action that is currently being run
        action_id (int): the server-assigned id of the action that is currently being run
        target_angle (int): the angle we wish to turn to
    """
    turn_commands = ["left", "right"]
    global SERVO_ANGLE
    if abs(target_angle) > MAX_SERVO_ANGLE:
        print("MAX TURN EXCEEDED!")
        return

    start_angle = SERVO_ANGLE
    picarx = Picarx()
    step = -1 if start_angle > target_angle else 1

    # Slowly turn the servo; step determines what direction to turn
    for angle in range(start_angle, target_angle, step):
        picarx.set_dir_servo_angle(angle)
        SERVO_ANGLE = angle
        sleep(SLEEP_TIME)

        if has_new_turn_command(action, action_id):
            return

    # Turn back to neutral position after you've finished turning
    set_turn_angle(action, action_id, 0)


def turn_left(current_action: str, action_id: int) -> None:
    """Smoothly turns the car left

    Args:
        current_action (str): The current action being run
        action_id (int): The id of the current action being run
    """
    set_turn_angle(current_action, action_id, -1 * MAX_SERVO_ANGLE)


def turn_right(current_action: str, action_id: int) -> None:
    """Smoothly turns the car right

    Args:
        current_action (str): The current action being run
        action_id (int): The id of the current action being run
    """
    set_turn_angle(current_action, action_id, MAX_SERVO_ANGLE)


def has_new_command(current_action: str, action_id: int, command_array: list) -> bool:
    """Checks if the last received command is one of the commands in the list

    Args:
        current_action (str): the current action being run
        action_id (int): the id of current action being run
        command_array (list): the array of commands to check against

    Returns:
        bool: _description_
    """
    running_action = make_command(current_action, action_id)
    last_received_action = make_command(CURRENT_ACTION, CURRENT_ID)

    if current_action in command_array:
        return running_action != last_received_action

    return False


def has_new_move_command(current_action: str, action_id: int) -> bool:
    """Checks if we have a new move command

    Args:
        current_action (str): the current action being run
        action_id (int): the id of current action being run

    Returns:
        bool: _description_
    """
    return has_new_command(current_action, action_id, ["forward", "backward", "stop"])


def has_new_turn_command(current_action, action_id) -> bool:
    """Checks if we have a new move command i.e our new command is either left or right

    Args:
        current_action (str): the current action being run
        action_id (int): the id of current action being run

    Returns:
        bool: _description_
    """
    return has_new_command(current_action, action_id, ["left", "right"])


def move_motor(motor_spin: int, rate: int, action: str, action_id: int) -> None:
    """Moves the motor forward or backward and interrupts when a new move command is
    received

    Args:
        motor_spin (int): the amount to move the motor forward
        rate (int): rate the motor should move forward (also affects how stuttery the movement feels)
        action (str): current action being run
        action_id (int): the id of the current action being run
    """
    picar = Picarx()
    speed = motor_spin
    move_speed = speed * rate
    picar.forward(move_speed)
    sleep(0.1)
    
    # Gradually slows down if no new 'movement commands' are received
    while speed > 0:
        speed -= 1
        picar.forward(move_speed)
        print(move_speed)
        sleep(SLEEP_TIME)

        # Allows for continuous pressing of forward to go forward
        if has_new_move_command(action, action_id) and speed < 50:
            return

    stop_car(action, action_id)


def move_forward(action: str, action_id: int) -> None:
    """Moves the card forward and allows for this movement to be interrupted

    Args:
        action (str): current action being run
        action_id (int): the id of the current action being run
    """
    move_motor(action=action, action_id=action_id, motor_spin=100, rate=1)


def stop_car(action: str, action_id: int) -> None:
    """Stops the car

    Args:
        action (str): current action being run
        action_id (int): the id of the current action being run
    """
    picar = Picarx()
    picar.forward(0)


def move_backward(action: str, action_id) -> None:
    """Moves the card backwards and allows for this movement to be interrupted

    Args:
        action (str): current action being run
        action_id (int): the id of the current action being run
    """
    move_motor(action=action, action_id=action_id, motor_spin=100, rate=-1)


def make_command(action: str, action_id: int) -> str:
    """Creates a string in the format action:action_id allowing for quick comparison
    commands and their ids & easier logging

    Args:
        action (str): current action being run
        action_id (int): the id of the current action being run

    Returns:
        str: returns action:action_id
    """
    return f"{action}:{action_id}"


def do_action(action: str, action_id: int) -> None:
    """Runs a given action

    Args:
        action (str): action we wish to run
        action_id (int): server-assigned id of that action
    """
    global LAST_RUN_COMMMAND_ID
    action = action.lower()
    actions = init_actions()
    valid_action = action in actions.keys()

    # Don't attempt invalid actions
    if not valid_action:
        print("INVALID ACTION SENT")
        return

    # Execute action with given unit
    actions[action](action, action_id)
    LAST_RUN_COMMMAND_ID = action_id


def run_server():
    """Runs the server
    """
    mySock = socket(AF_INET, SOCK_DGRAM)
    mySock.bind(("", 12000))
    global CURRENT_ID
    global CURRENT_ACTION

    # Consistently receive packets from client
    while True:
        command, _ = mySock.recvfrom(2048)
        command = command.decode()
        CURRENT_ID += 1 # id allows differntiating of commands on the client side
        CURRENT_ACTION = command

        print(f"Command Received: {make_command(command, CURRENT_ID)}")


def run_actions():
    """Runs all the actions received from the client
    """
    while True:
        current_command = CURRENT_ACTION
        current_id = CURRENT_ID

        # Don't keep repeating the same action
        if current_id != LAST_RUN_COMMMAND_ID:
            print(f"executing action: {make_command(current_command, current_id)}")
            do_action(current_command, current_id)


def main():
    """Main function - initializes the server and action threads
    to allow simultaneous listening and execution of actions"""
    server_thread = threading.Thread(target=run_server)
    movement_thread = threading.Thread(target=run_actions)

    server_thread.start()
    movement_thread.start()


if __name__ == "__main__":
    main()
