from path import Path
import jinja2
import smtpd
import json
import re
import sys


if sys.version_info[0] >= 3:
    from email.parser import Parser
else:
    from email.Parser import Parser


THIS_DIRECTORY = Path(__file__).realpath().dirname()


class MockSMTPServer(smtpd.SMTPServer):
    """Mock SMTP server."""
    def __init__(self, *args, **kwargs):
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        self.counter = 0

    def process_message(self, host, email_from, email_to, data, **kwargs):
        """Parse SMTP message and log it to the console as JSON."""
        if sys.version_info[0:2] >= (3, 6):
            parsed_message = Parser().parsestr(data.decode('utf8'))
        else:
            parsed_message = Parser().parsestr(data)
        
        #links_regex = re.compile(r"(https?://\S+)")

        if parsed_message.is_multipart():
            payload = []
            for message in parsed_message.get_payload():
                payload_dict = dict(message)
                payload_dict['filename'] = message.get_filename()
                payload_dict['content'] = message.get_payload(decode=True).decode("utf-8")
                payload.append(payload_dict)
        else:
            payload = parsed_message.get_payload()

        header_from = parsed_message.get('From')
        header_to = parsed_message.get('To')
        email_regex = re.compile(r"^(.*?)\<(.*?)\>$")

        if header_from:
            header_from_name = email_regex.match(header_from).group(1).strip()\
                if email_regex.match(header_from) else None
            header_from_email = email_regex.match(header_from).group(2)\
                if email_regex.match(header_from) else None
        else:
            header_from_name = header_from_email = None

        if header_to:
            header_to_name = email_regex.match(header_to).group(1).strip()\
                if email_regex.match(header_to) else None
            header_to_email = email_regex.match(header_to).group(2)\
                if email_regex.match(header_to) else None
        else:
            header_to_name = header_to_email = None

        dict_message = {
            'sent_from': email_from,
            'sent_to': email_to,
            'header_from': header_from,
            'header_to': header_to,
            'header_from_name': header_from_name,
            'header_to_name': header_to_name,
            'header_from_email': header_from_email,
            'header_to_email': header_to_email,
            'subject': parsed_message.get('Subject'),
            'date': parsed_message.get('Date'),
            'contenttype': parsed_message.get_content_type(),
            'multipart': parsed_message.is_multipart(),
            'payload': payload,
        }

        self.counter = self.counter + 1
        Path("{0}.message".format(self.counter)).write_text(
            json.dumps(dict_message, indent=4)
        )
        
        Path("{0}.html".format(self.counter)).write_text(
            jinja2.Template(
                THIS_DIRECTORY.joinpath("email.jinja2").text()
            ).render(**dict_message)
        )

        sys.stdout.write(json.dumps(dict_message))
        sys.stdout.write('\n')
        sys.stdout.flush()

        """
        if len(email_to) > 0:
            if email_to[0].endswith("@smtperrors.com"):
                name = email_to[0].replace("@smtperrors.com", "")
                if name in smtperrors.errors:
                    return smtperrors.errors[name]
                else:
                    raise Exception("{0} was not found in the list of SMTP errors.")
        """
