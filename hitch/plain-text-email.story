Receive plain text email:
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
      subject: my subject
      plain message: my message
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
            "subject": "my subject",
            "date": "Sat, 26 May 2018 09:00:00 +0000",
            "contenttype": "text/plain",
            "multipart": false,
            "payload": "my message"
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
            <div class="col-sm-6 bg-primary"><h4>From: alice@example.org</h4></div>
            <div class="col-sm-6 bg-primary"><h4>To: bob@example.org</h4></div>
          </div>
          <div class="row">
            <div class="col-sm-12 bg-primary"><h4>Subject: my subject</h4></div>
          </div>
          
          <div class="row">
             <div class="col-sm-12"><h4>Plaintext email</h4></div>
          </div>
          <div class="row">
            <div class="col-sm-12">
            my message
            </div>
          </div>
          
        </div>
        </body>
        </html>
