""" Production system starting module """

import sys
from production_system.controller.classification_system import ClassificationSystem

if __name__ == '__main__':

    classification_system = ClassificationSystem()
    try:
        classification_system.run()
    except KeyboardInterrupt:
        print("Segregation App terminated")
        sys.exit(0)
