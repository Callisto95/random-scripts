import logging
import sys
from argparse import ArgumentParser, Namespace

from obsws_python import ReqClient
from notify_send_py.notify_send_py import NotifySendPy

if len(sys.argv) <= 1:
	print("no command received")
	exit(1)

# obsws is printing errors by default
logging.disable()

try:
	client: ReqClient = ReqClient(host="localhost", port=4455, password="PASSWORD")
except ConnectionRefusedError:
	NotifySendPy().notify("Error: connection refused", "Cannot connect to OBS, is it running?", app_name="OBSPY")
	exit(3)

parser: ArgumentParser = ArgumentParser()
parser.add_argument("mode", choices=["save-replay"])

args: Namespace = parser.parse_args()

try:
	match args.mode:
		case "save-replay":
			client.save_replay_buffer()
		case _:
			print(f"unknown command '{args.mode}'")
			exit(2)
except Exception as exc:
	NotifySendPy().notify("Error: an exception was thrown!", f"{exc}", app_name="OBSPY")
