import argparse

from mbeam import manager
from mbeam import webserver


def get_parser():
    parser = argparse.ArgumentParser(description='mbeam server')
    parser.add_argument('-p','--port', help='Port to listen on', default=2001)
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    mgr = manager.Manager()
    mgr.start()

    websrv = webserver.WebServer(mgr, args.port)
    websrv.start()
