Receive simple email:
  description: |
    This story demonstrates PretendSMTP receiving an
    email and dumping it to file.
  given:
    python version: 3.5.0
    setup: |
      from pretendsmtp import pretend_smtp_server
      import smtplib
      import time
      
      server = pretend_smtp_server(port="10025").in_dir("mail").pexpect()
      server.expect("SMTP SERVER RUNNING")
  steps:
  - Run: |
      import q
      q('1')
      #print(server.read().decode('utf8'))
      q('2')
      import time
      time.sleep(0.5)
      smtp_sender = smtplib.SMTP('localhost', 10025)
      smtp_sender.sendmail(
          "alice@example.org",
          ["bob@example.org"],
          "message"
      )
      q('3')
      time.sleep(0.5)
      server.kill(9)
  - Files present:
      files:
        mail/1.message: message
