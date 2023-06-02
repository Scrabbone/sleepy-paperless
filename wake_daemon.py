from datetime import datetime
import os

INBOX = "./gunicorn/gunicorn-daemon"

CMD = "docker container unpause paperless-db paperless-broker paperless-webserver"

print("Waiting for wake call...")

def get_time_s():
	now = datetime.now()
	return "{hour}:{minute}:{second} {day}.{month}.{year} -> ".format(hour=now.hour,minute=now.minute,second=now.second,day=now.day,month=now.month,year=now.year)

while True:
	with open(INBOX, "r", encoding="utf-8") as f:
		while True:
			s = f.read()
			print(get_time_s()+str(s))
			if len(s) <= 0: break
			s = s.split("\n")
			if(s[len(s)-2] == "wake up"):
				print(get_time_s()+" Executing: "+CMD)
				c = os.system(CMD)
				print("response-code: "+str(c))
