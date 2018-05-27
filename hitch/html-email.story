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
            "date": "Sat, 26 May 2018 09:00:00 +0000",
            "contenttype": "multipart/alternative",
            "multipart": true,
            "payload": [
                {
                    "filename": null,
                    "content-type": "text/plain",
                    "content-charset": "utf-8",
                    "transfer-encoding": "base64",
                    "content": ""
                },
                {
                    "filename": null,
                    "content-type": "text/html",
                    "content-charset": "utf-8",
                    "transfer-encoding": "base64",
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
            <div class="col-sm-4"><h4>From: alice@example.org</h4></div>
            <div class="col-sm-4"><h4>To: bob@example.org</h4></div>
          </div>
          <div class="row">
            <div class="col-sm-8"><h4>Subject: My subject</h4></div>
          </div>
          
          
          <div class="row">
            <div class="col-sm-8"><h4>text/plain</h4></div>
          </div>
          
          <div class="row">
            <div class="col-sm-8">
                
            </div>
          </div>
          
          
          <div class="row">
            <div class="col-sm-8"><h4>text/html</h4></div>
          </div>
          
          <div class="row">
            <div class="col-sm-8">
                <html><body>My HTML message</body></html>
            </div>
          </div>
          
          
          
        </div>
        </body>
        </html>
