import sys
import mbeam


def main():
    port = 2001
    if len(sys.argv) == 2:
        port = sys.argv[1]

    manager = mbeam.Manager()
    manager.start()

    webserver = mbeam.WebServer(manager, port)
    webserver.start()
