from picarx import Picarx
import time

def main():
    picar = Picarx()
    picar.forward(-50)
    time.sleep(1)
    picar.forward(0)
    pass

if __name__ == "__main__":
    main()
