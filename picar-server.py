from socket import *

ACTIONS = ["FORWARD", "BACKWARD", "LEFT", "RIGHT"]

def do_action(action, unit):
    pass


def take_action(client_command: str) -> None:
    action = client_command.split(":")[0]
    unit = int(client_command.split(":")[1])
    valid_action = action in ACTIONS;

    # Quit if action is not valid
    if not valid_action:
        return;

    do_action(action, unit)
    return


def main():
    mySock = socket(AF_INET,SOCK_DGRAM)
    mySock.bind(('', 12000))

    while True:
        message, clientAddress = mySock.recvfrom(2048)
        message = message.decode()
        take_action(message)
        mySock.sendto("got it".encode(), clientAddress)

if __name__ == "__main__":
    main()
