Receive simple email:
  description: |
    This story demonstrates PretendSMTP receiving an
    email and dumping it to file.
  steps:
  - Start server: |
      from pretendsmtp import pretend_smtp_server
      
      pretend_smtp_server().in_dir("mail").run()
  - Sleep: 0.5
  - Send email to localhost:
      from mail: alice@example.org
      to mails:
        - bob@example.org
      message: message
      port: 10025
  - Files present:
      files:
        mail/1.message: message
