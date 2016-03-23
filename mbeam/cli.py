import sys

from mbeam import manager
from mbeam import webserver


def main():
    port = 2001
    if len(sys.argv) == 2:
        port = sys.argv[1]

    mgr = manager.Manager()
    mgr.start()

    websrv = webserver.WebServer(mgr, port)
    websrv.start()
