#!/usr/bin/python

from time import sleep

from requests import get, Response
from requests.exceptions import ConnectionError

while True:
	try:
		req: Response = get("https://www.google.com")
		print(req)
	except ConnectionError:
		pass
	finally:
		sleep(60)
