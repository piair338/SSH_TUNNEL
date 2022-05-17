PortIn =  # sur la machine locale
PortOut =  # sur la machine distante
IP = 



OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'



from datetime import date
import re
import subprocess
from time import sleep, asctime
from typing import Match
from os import path, sep, getlogin


sshKey = path.expanduser(sep.join(["~"+getlogin(),".ssh","id_rsa"])) # a changer par le chemin de la clé id_rsa si pas a cet endroit


def escape_ansi(line):
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)


process = subprocess.Popen(['ssh',"-i",sshKey,"-R", f"{PortOut}:127.0.0.1:{PortIn}",f'pi@{IP}',"-tt"], stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,universal_newlines=True)

def execute(cmd) :
    process.stdin.write(cmd+'\n')
    process.stdin.flush()

def install(prog):

    print(FAIL + f"il manque le programme {prog}. il faut l'installer." + ENDC)
    print(OKBLUE+"installation en cours"+ENDC)
    execute(f"sudo apt install {prog}")


def PortDejaPris() :
    print(f"{FAIL}le tunnel n'a pas pu demarrer, le port étais déjà pris{ENDC}")
    KillPort()
    sleep(1)

    #process = subprocess.Popen(['ssh',"-R", f"{PortOut}:127.0.0.1:{PortIn}",f'pi@{IP}',"-tt"], stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,universal_newlines=True)


def ServerClosed():
    print(f"{FAIL}-- connection to {IP} closed by remote host. --{ENDC}")

def ServerRefused() :
    print(f"{FAIL}-- Connection refused --{ENDC}")

def ConnectionClosed() :
    print(f"{FAIL}-- ConnectionClosed --{ENDC}")

def KillPort() :
    print(OKCYAN + 'tentative de kill' + ENDC)
    execute(f'sudo lsof -ti:{PortOut} | xargs kill -9')
    execute('logout')
    print(OKGREEN + 'port libéré' + ENDC)



while True:
    try :
        output = process.stdout.readline()
        output = output.replace('pi@raspberrypi:~ $',"")
        output = output.replace('\n',"").replace('\x1b]0;pi@raspberrypi: ~\x07 ',"")
        print(OKBLUE + output + ENDC)


        if output== f"Warning: remote port forwarding failed for listen port {PortOut}" :
            PortDejaPris()
        elif output == f"Connection to {IP} closed by remote host." :
            ServerClosed()
        elif output ==f"ssh: connect to host {IP} port 22: Connection refused" :
            ServerRefused()
        elif output ==f"ssh: connect to host {IP} port 22: Connection timed out" :
            ServerRefused()
        elif output ==f"Connection to {IP} closed." :
            ConnectionClosed()

        if output == "-bash: lsof: command not found" :
            install('lsof')


        return_code = process.poll()
        if return_code is not None:
            print('execution terminée. 30sec avant de relancer.')
            sleep(30)
            process = subprocess.Popen(['ssh', "-i",sshKey,"-R", f"{PortOut}:127.0.0.1:{PortIn}",f'pi@{IP}',"-tt"], stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,universal_newlines=True)
    except KeyboardInterrupt as error :
        print(OKCYAN + "\nTunnel fermé" + ENDC)
        break
