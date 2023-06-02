<h3 align="center">Sleepy Paperless-NGX</h3>
<h4 align="center">A small setup to put paperless to sleep when not in use and thus spindown the hard drives</h4>

---

# 🧾Table of contents

- [Introduction](#-introduction)
- [Setup](#-setup)
- [Uninstall](#-uninstall)
- [Thanks](#-thanks)

# 🔭 Introduction

I use the wonderful paperless-ngx project on a raspberry pi 4 myself to archive my documents. Unfortunately, the postgresql database prevents the spindown of the HDDs. For this reason, I came up with this solution. I changed the [docker-compose.yml](/docker-compose.yml) file and added two additional container and python scripts to pause the paperless-ngx containers. With a call to ```http://[hostname]:8080/wake_up```, Paperless is started and remains running as long as the service is used. If the service idles for a long time, it is paused to save energy and let the HDDs spindown.

# 🛠️ Setup

<b style="color: coral">Please test the setup with a test system before you put it on your productive archiving system with your important files. The archive system is accessed via http at the end and the transmission is therefore unencrypted. Therefore, do not use the project outside of a secured area, such as a LAN</b>

0. If not installed yet, install docker and docker compose

    ```bash
    wget https://get.docker.com -O - | sudo bash
    ```

    to run docker commands without typing sudo, you have to create a new group named 'docker'

    ```bash
    sudo groupadd docker
    ```

    now add your current user to the docker group

    ```bash
    sudo usermod -aG docker $USER
    ```

    and load the changes you made

    ```bash
    newgrp docker
    ```

    now you have successfully installed docker 🥳

1. Please check out the official [paperless-ngx repository](https://github.com/paperless-ngx/paperless-ngx#getting-started) and read the docker-compose installation instructions before you begin.

2. Clone the repository into a directory where you want to store your docker directories
    ```bash
    git clone https://github.com/Scrabbone/sleepy-paperless.git
    ```

3. Check the [docker-compose.env](/docker-compose.env) file 
    
    ```bash
    cd sleepy-paperless
    ```

    and adjust the settings. In particular, you should set the value PAPERLESS_SECRET_KEY in line 27, PAPERLESS_ADMIN_USER in line 38 and PAPERLESS_ADMIN_PASSWORD in line 39. The values are currently dummy values

    ```bash
    nano docker-compose.env
    ```
    you can also use ```vim``` as ```nano``` for example

4. You have to change the hostname in [app.y](/gunicorn/app.py) to the hostname of the machine where your docker runs. Get the hostname of your machine with

    ```bash
    hostname
    ```

    You have to copy this name into the [app.y](/gunicorn/app.py) at line 4

    ```bash
    nano gunicorn/app.py
    ```

4. Create a user
    ```bash
    docker-compose run --rm webserver createsuperuser
    ```
    now your admin account that you configured in the [docker-compose.env](/docker-compose.env) file will be created and you will be asked for a new user creation that you can use to login at the frontpage of paperless

5. Create a named pipe for the wsgl server

    ```bash
    cd gunicorn && mkfifo gunicorn-daemon -m600 && cd ..
    ```

6. Finally start the docker composition 🚀

    ```bash
    docker-compose up -d
    ```

7. Check whether your paperless-ngx is server is working. Type

    ```http://[hostname]:8080/```

    into your browser. \
    You should see the login page. Try to login with your user credentials that you saved in step 4

8. Start a shell with for example tmux. If tmux is not installed yet type:

    ```bash
    sudo apt-get install tmux -y
    ```
    Start the shell with
    ```bash
    tmux
    ```

10. Now run the [sleep_daemon.py](/sleep_daemon.py) script. The ```20``` is the cpu utilisation rate in percent, which must be permanently undercut by the paperless container in order to sleep paperless. ```900``` is the duration in seconds for which the cpu must not have been loaded by the paperless container more than the previously specified limit value.
    ```bash
    python3 sleep_daemon.py 20 900
    ```
    and start a new Shell with ```Ctrl+B``` and then type ```c```

12. Start the [wake_daemon.py](/wake_daemon.py) script
    ```bash
    python3 wake_daemon.py
    ```

13. Now test if the system works. \

    Go back to your browser and type 

    ```http://[hostname]:8080/wake_up```

    You should now be redirected to the paperless-ngx website.

14. You can finetune your threshold of step 10 to let paperless-ngx sleep at perfect time. Open a new shell with ```Ctrl+B``` and ```c``` and then type

    ```bash
    docker stats
    ```

    Now do something on the paperless-website in your browser and look at the cpu utilisation. You can close the stats with ```Ctrl+C```. If you think you found a good value, navigate to your first tmux window with ```Ctrl+B``` and ```0``` and terminate the [sleep_daemon.py](/sleep_daemon.py) with ```Ctrl+c```. Then restart the program with your new value and check again. You can suspend tmux to background with ```Ctrl+B``` and ```d``` and open your session with 

    ```bash
    tmux attach-session
    ```

If you are satisfied, you can leave the start-up to cron so that you don't have to worry about your HDD running all day again when you reboot. I have placed the repository in ```/home/pi/sleepy-paperless/```. If the paths have different names, you should adapt the following commands. Copy the following command

```bash
@reboot cd /home/pi/sleepy-paperless > /dev/null 2> /dev/null && docker compose up -d > /dev/null 2> /dev/null
@reboot cd /home/pi/sleepy-paperless > /dev/null 2> /dev/null && python3 sleep_daemon.py 20 900 > /dev/null 2> /dev/null
@reboot cd /home/pi/sleepy-paperless > /dev/null 2> /dev/null && python3 wake_daemon.py > /dev/null 2> /dev/null
```

and paste it in

```bash
crontab -e
```

<a style="color: gray">HINT: Do not forget to set the PATH Variable before the cronjob commands. First copy your PATH content with ```echo $PATH``` and then paste it before the given commands in your ```crontab -e``` e.g ```PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games```</a>

# 🧹 Uninstall

1. First make sure that your containers do not run

    ```bash
    docker compose down
    ```

2. Type following to uninstall docker

    ```bash
    sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
    ```

    and remove all other docker directories

    ```bash
    sudo rm -rf /var/lib/docker
    sudo rm -rf /var/lib/containerd
    ```

3. Remove the git repo with all files. <a style="color: coral">WARNING: Be careful, all your files will be deleted and by that I mean your entire paperless archive!</a>

    ```bash
    sudo rm -rf sleepy-paperless
    ```

# 🙏 Thanks

I would like to thank the developers of the paperless-ngx project. Please check out the official project [paperless-ngx](https://github.com/paperless-ngx/paperless-ngx/tree/dev)