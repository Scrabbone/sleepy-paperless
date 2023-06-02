import os
import time
import json
import argparse
from multiprocessing import Process
from datetime import datetime

PIPE = "./stats"
CHECK_INTERVAL = 1 #seconds
CONTAINER = "paperless-webserver"
CMD = "docker stats --no-stream --format '{{ json . }}' "+CONTAINER
SLEEP_CMD = "docker container pause paperless-webserver paperless-broker paperless-db"

parser = argparse.ArgumentParser("Spectates container for idling.")
parser.add_argument("threshold", default="20.0", help="Threshold decides whether process idles.")
parser.add_argument("max", default="900", help="Maximal idle time in seconds.")
args = parser.parse_args()

threshold = 1.0
try:
	threshold = float(args.threshold)
except Exception as e:
	print("Treshold is not in float castable")
	exit(-1)

if threshold > 100.0 or threshold < 0.0:
	print("Threshold is too small.")
	exit(-1)

max_idle_time = 1_000_000
try:
	max_idle_time = float(args.max)
except Exception as e:
	print("Max IDLE time is not in float castable.")
	exit(-1)

if max_idle_time < 10.0:
	print("Max IDLE time is too small.")
	exit(-1)

if not os.path.exists(PIPE):
	if os.system("mkfifo -m600 "+PIPE) < 0:
		print("The pipe is not reachable and could not be created.")
		exit(-1)
# Get Pause state of container. Returns True iff container pause state was not readable
def get_paused(container):
	def cmd():
		os.system("docker container inspect "+container+" --format '{{ json .State }}' > ./stats")
	p = Process(target=cmd, args=tuple([]))
	p.start()
	with open("stats","r",encoding="utf-8") as f:
		s = f.read()
	state = True
	try:
		state = json.loads(s)
		state = state["Paused"]
	except Exception as e:
		pass
	return state

def get_time_s():
	now = datetime.now()
	return "{hour}:{minute}:{second} {day}.{month}.{year} -> ".format(hour=now.hour,minute=now.minute,second=now.second,day=now.day,month=now.month,year=now.year)

def kickoff_observer():
	def system_cmd():
		os.system(f"{CMD} > {PIPE}")
	p = Process(target=system_cmd, args=tuple([]))
	p.start()



def get_cpu_usage(container):
	kickoff_observer()
	with open(PIPE, "r", encoding="utf-8") as f:
		s = f.read()
	usage = ""
	try:
		stats = json.loads(s)
		usage = stats["CPUPerc"][0:-1]
	except Exception as e:
		print(get_time_s()+"NOT_FOUND")
	
	usage_f = 0.0
	try:
		usage_f = float(usage)
	except Exception as e:
		pass
	print(f"{get_time_s()}cpu usage: {usage_f}")
	return usage_f


# Check for idle
first_idle = 0.0
first_run = True
while True:
	# Check container state
	paused_b = get_paused(CONTAINER)
	if not paused_b:
		cpu_usage_f = get_cpu_usage(CONTAINER)

		if cpu_usage_f < threshold:
			print(get_time_s()+"IDLE")
			if first_idle <= 0.0:
				first_idle = datetime.now().timestamp()
			else:
				now = datetime.now().timestamp()
				if (now - first_idle) > max_idle_time:
					print(f"{get_time_s()}Executing: {SLEEP_CMD}")
					os.system(SLEEP_CMD)
		else:
			print(f"{get_time_s()}WORK")
			first_idle = 0.0
	else:
		print(f"{get_time_s()}PAUSED")
		first_idle = 0.0
	if not first_run:
		time.sleep(CHECK_INTERVAL)
	first_run = False
	
