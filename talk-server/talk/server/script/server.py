import argparse
import talk.server


parser = argparse.ArgumentParser()

parser.add_argument('--port', default=9090, type=int)
parser.add_argument('--ssl', default=False, type=bool)

arguments = parser.parse_args()


def run():
    talk.server.open(arguments.port)
