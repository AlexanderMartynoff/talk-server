import argparse
import talk.server.client


parser = argparse.ArgumentParser()

parser.add_argument('--port', default=9090, type=int)
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--ssl', default=False)
parser.add_argument('--user')

arguments = parser.parse_args()


def run() -> None:
    talk.server.client.open(arguments.host, arguments.port, arguments.user)
