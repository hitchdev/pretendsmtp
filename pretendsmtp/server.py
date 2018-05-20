from commandlib import python_bin
from pretendsmtp.mock_server import MockSMTPServer
from path import Path
import asyncore
import signal
import sys
import os


INCLUDE_PATH = Path(__file__).realpath().dirname() / "include"


def pretend_smtp_server(port="10025"):
    return python_bin.pretendsmtp(port)


def main():
    port_number = int(sys.argv[1])
    if port_number < 1024:
        sys.stderr.write("WARNING: Using a port below 1024 to run test Internet services"
                         " on is normally prohibited for non-root users, "
                         " and usually inadvisable.\n\n")
        sys.stderr.flush()

    INCLUDE_PATH.copytree(Path(os.getcwd()) / "include")

    smtp_server = MockSMTPServer(('localhost', port_number), None)

    def signal_handler(signal, frame):
        print('')
        smtp_server.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    sys.stdout.write("SMTP SERVER RUNNING\n")
    sys.stdout.flush()
    asyncore.loop()
