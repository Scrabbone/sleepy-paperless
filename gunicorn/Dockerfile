FROM ubuntu
RUN apt update && apt-get dist-upgrade -y && apt-get install python3 -y && apt-get install python3-pip -y
RUN alias python=python3
RUN pip3 install gunicorn
VOLUME /home/app.py
VOLUME /home/pipe
WORKDIR /home/
CMD ["gunicorn", "-n", "myunicorn", "-b", "0.0.0.0:6000", "app:app"]
