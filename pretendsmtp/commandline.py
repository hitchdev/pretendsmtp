from commandlib import python_bin
from pretendsmtp.mock_server import MockSMTPServer
from path import Path
import asyncore
import signal
import sys
import os


INCLUDE_PATH = Path(__file__).realpath().dirname() / "include"


def pretend_smtp_server(port="10025"):
    return python_bin.pretendsmtp("server", port)


def main():
    if sys.argv[1] == "server":
        port_number = int(sys.argv[2])
        if port_number < 1024:
            sys.stderr.write(
                "WARNING: Using a port below 1024 to run test Internet services"
                " on is normally prohibited for non-root users, "
                " and usually inadvisable.\n\n"
            )
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
    elif sys.argv[1] == "forwardlast":
        import argparse
        import json
        parser = argparse.ArgumentParser()
        parser.add_argument("command", help="what to make pretendsmtp do")
        parser.add_argument("host", help="SMTP host")
        parser.add_argument("--username", type=str, help="SMTP username")
        parser.add_argument("--password", type=str, help="SMTP password")
        parser.add_argument("--port", type=int, help="SMTP port")
        parser.add_argument("--from_email", type=str, help="Address to forward email from")
        parser.add_argument("--to_email", type=str, help="Address to forward email to")
        args = parser.parse_args()
        last_email_number = max([
            int(filepath.basename().splitext()[0])
            for filepath in Path(".").listdir("*.message")
        ])
        email_data = json.loads(Path("{0}.message".format(last_email_number)).text())
        import smtplib

        from email.mime.multipart import MIMEMultipart
        from email.mime.multipart import MIMEBase

        message = MIMEMultipart('alternative')

        for part in email_data['payload']:
            maintype, subtype = part['content-type'].split("/")
            mimepart = MIMEBase(maintype, subtype)
            mimepart.set_payload(part['content'])
            message.attach(mimepart)

        message['Subject'] = email_data['subject']
        message['From'] = args.from_email
        message['To'] = args.to_email

        smtp_server = smtplib.SMTP(
            args.host,
            port=args.port,
        )
        
        if args.username is not None:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(args.username, args.password)

        smtp_server.send_message(message)
        smtp_server.quit()
    else:
        sys.stderr.write("Usage : pretendsmtp server 10025")
        sys.exit(1)
