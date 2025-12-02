import sys
from development_system.src.development_system import DevelopmentSystem

if __name__ == '__main__':

    development_system = DevelopmentSystem()
    try:
        development_system.run()
    except KeyboardInterrupt:
        print("Development App terminated")
        sys.exit(0)