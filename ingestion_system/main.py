import sys
from ingestion_system.src.ingestion_system import IngestionSystem

if __name__ == '__main__':

    ingestion_system = IngestionSystem()
    try:
        ingestion_system.run()
    except KeyboardInterrupt:
        print("Segregation App terminated")
        sys.exit(0)