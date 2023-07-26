import paramiko
import sys
import threading
import time

from colorama import init
init(autoreset=True)
from colorama import Fore, Back, Style


BASE_LOGIN = "admin"
BASE_PASSWORD = "admin"


class SSHClient:
	def __init__(self, host, port, login=None, password=None, logs=False):
		self.LOGS = logs
		self.login = BASE_LOGIN if not login else login
		self.password = BASE_PASSWORD if not password else password

		self.host = host
		self.port = port

		self.GETTING = True
		self.stdin, self.stdout, self.stderr = None, None, None


	def startClient(self):
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		if self.LOGS: print(Fore.GREEN + '[+] Client has been created.')

		try:
			self.client.connect(
					hostname=self.host, port=self.port, 
					username=self.login, password=self.password
				)

			if self.LOGS: print(Fore.GREEN + f'[+] Client has been connected to {self.host}:{self.port}.')

			return self, 1
		except Exception as error: return error, None


	def printGettedData(self, delay=0.1):
		while self.GETTING:
			try:
				data = self.stdout.read().decode()
				if data: print(Fore.GREEN + '\n' + data)

				self.stdout = None
			except Exception as error: pass

			time.sleep(delay)

	def sendCommand(self, command, getoutput=True):
		self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
		if getoutput:
			output = stdout.read() + stderr.read()
			return output


	def close(self):
		if self.LOGS: print(Fore.GREEN + '\n[+] Closing...')
		self.GETTING = False
		self.client.close()
		if self.LOGS: print(Fore.GREEN + '[+] SSH has been closed.')



def getElementByPrefix(argv, prefix):
	try: return argv[argv.index(prefix) + 1]
	except: pass


def main(argv):
	path = '/'

	try: host, port = argv[1].split(':')
	except:
		print(Fore.RED + '[-] Host/post has not been found.')
		exit()

	port = int(port)
	login = getElementByPrefix(argv, '-l')
	password = getElementByPrefix(argv, '-p')


	client, result = SSHClient(host, port, login=login, password=password, logs=True).startClient()

	if result:
		threading.Thread(target=client.printGettedData).start()

		while True:
			try:
				command = input(f'{host}:{port} > ')

				if command == '': pass

				elif 'cd' in command.split(' '):
					if command.split(' ')[command.split(' ').index('cd') + 1] == '..':
						if path != '/':
							path = '/' + '/'.join(path[1:-1].split('/')[:-1])
					else:
						addsl = "/" if path[-1] != "/" else ""
						path = path +  addsl + f'{" ".join(command.split(" ")[command.split(" ").index("cd") + 1:])}/'

				else:
					client.sendCommand(command + f' -c {path}', getoutput=False)
					# print(Fore.GREEN + output.decode())

			except KeyboardInterrupt:
				client.close()
				break

	else:
		print(Fore.RED + f'{client}')



if __name__ == '__main__': main(sys.argv)
