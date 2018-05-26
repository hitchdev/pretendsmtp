Receive HTML email:
  description: |
    This story demonstrates PretendSMTP receiving an
    email and dumping it to file as JSON.
  steps:
  - Start server:
      code: |
        from pretendsmtp import pretend_smtp_server

        pretend_smtp_server().in_dir("mail").run()
      and wait until code prints: SMTP SERVER RUNNING
  - Send email:
      from mail: alice@example.org
      to mails:
      - bob@example.org
      subject: My subject
      plain message: Plain message alternative
      html message: <html><body>My HTML message</body></html>
      port: 10025
  - Sleep: 0.5
  - JSON File present:
      filename: mail/1.message
      content: |-
        {
            "sent_from": "alice@example.org",
            "sent_to": [
                "bob@example.org"
            ],
            "header_from": "alice@example.org",
            "header_to": "bob@example.org",
            "header_from_name": null,
            "header_to_name": null,
            "header_from_email": null,
            "header_to_email": null,
            "subject": "My subject",
            "date": "Sat, 26 May 2018 08:59:02 +0000",
            "contenttype": "multipart/alternative",
            "multipart": true,
            "payload": [
                {
                    "Content-Type": "text/plain; charset=\"utf-8\"",
                    "MIME-Version": "1.0",
                    "Content-Transfer-Encoding": "base64",
                    "filename": null,
                    "content": "Plain message alternative"
                },
                {
                    "Content-Type": "text/html; charset=\"utf-8\"",
                    "MIME-Version": "1.0",
                    "Content-Transfer-Encoding": "base64",
                    "filename": null,
                    "content": "<html><body>My HTML message</body></html>"
                }
            ]
        }

  - HTML File present:
      filename: mail/1.html
      content: |-
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <title>Email</title>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link rel="stylesheet" href="include/bootstrap-3.3.7.min.css">
        </head>
        <body>

        <div class="container-fluid">
          <div class="row">
            <div class="col-sm-4">From: alice@example.org</div>
            <div class="col-sm-4">To: bob@example.org</div>
          </div>
          <div class="row">
            <div class="col-sm-8">Subject: My subject</div>
          </div>
          <div class="row">
            [{'Content-Type': 'text/plain; charset="utf-8"', 'MIME-Version': '1.0', 'Content-Transfer-Encoding': 'base64', 'filename': None, 'content': 'Plain message alternative'}, {'Content-Type': 'text/html; charset="utf-8"', 'MIME-Version': '1.0', 'Content-Transfer-Encoding': 'base64', 'filename': None, 'content': '<html><body>My HTML message</body></html>'}]
          </div>
        </div>
        </body>
        </html>
