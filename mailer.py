#!/usr/bin/python


import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

class mailer:

	@staticmethod
	def mail(to, subject, text, attach, gmail_usr, gmail_pwd):
		msg = MIMEMultipart()
		msg['From'] = gmail_usr
		msg['To'] = to
		msg['Subject'] = subject
		msg.attach(MIMEText(text))

		for file in attach:
			part = MIMEBase('application', 'octet-stream')
			part.set_payload(open(file, 'rb').read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename=%s' % os.path.basename(file))
			msg.attach(part)

		mailServer = smtplib.SMTP('smtp.gmail.com', 587)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login(gmail_usr, gmail_pwd)
		mailServer.sendmail(gmail_usr, to, msg.as_string())
		mailServer.close()