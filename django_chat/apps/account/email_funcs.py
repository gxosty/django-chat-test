import smtplib, ssl

class EmailVerificator:
	email = None
	password = None

	host = "smtp.gmail.com"
	port = 465

	context = None
	server = None

	def __init__(self, email, password):
		self.email = email
		self.password = password

		self.context = ssl.create_default_context()
		self.server = smtplib.SMTP_SSL(self.host, self.port, context = self.context)
		self.login()

	def login(self):
		try:
			self.server.login(self.email, self.password)
			print("[EV] EmailVerificator logged in as:", self.email)
		except Exception as ex:
			print("[EV] EmailVerificator couldn't login as:", self.email, "\n" + str(ex))

	def send_to(self, email, message):
		retries = 3
		while retries:
			try:
				print('[EV] Sending email to:', email)
				self.server.sendmail(self.email, email, message)
				print('[EV] Sent email to:', email)
				retries = 0
			except:
				retried -= 1
				print('[EV] Retrying...')
				self.login()