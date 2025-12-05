import sys
from test_system.src.test_system import TestSystem

if __name__ == '__main__':

    testSystem = TestSystem()
    try:
        testSystem.run()
    except KeyboardInterrupt:
        print("Test system terminated")
        sys.exit(0)