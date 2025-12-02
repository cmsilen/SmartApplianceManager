import sys
from production_system.src.production_system import ProductionSystem

if __name__ == '__main__':

    production_system = ProductionSystem()
    try:
        production_system.run()
    except KeyboardInterrupt:
        print("Segregation App terminated")
        sys.exit(0)