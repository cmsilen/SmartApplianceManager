import sys
from preparation_system.src.preparation_system import PreparationSystem

if __name__ == '__main__':

    preparation_system = PreparationSystem()
    try:
        preparation_system.run()
    except KeyboardInterrupt:
        print("Segregation App terminated")
        sys.exit(0)