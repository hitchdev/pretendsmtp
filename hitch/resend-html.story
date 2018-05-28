Resend HTML email:
  based on: receive html email
  description: |
    This story demonstrates receiving an email and then
    forwarding it on to the same server again.
  steps:
  - Run pretendsmtp:
      args:
      - forwardlast
      - localhost
      - --port
      - 10025
      - --from
      - testfrom@example.org
      - --to
      - testto@example.org

  - Sleep: 0.5
  
  - JSON File present:
      filename: mail/2.message
      content: |-
        {
            "sent_from": "testfrom@example.org",
            "sent_to": [
                "testto@example.org"
            ],
            "header_from": "testfrom@example.org",
            "header_to": "testto@example.org",
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
                    "content-charset": null,
                    "transfer-encoding": null,
                    "content": ""
                },
                {
                    "filename": null,
                    "content-type": "text/html",
                    "content-charset": null,
                    "transfer-encoding": null,
                    "content": "<html><body>My HTML message</body></html>"
                }
            ]
        }
