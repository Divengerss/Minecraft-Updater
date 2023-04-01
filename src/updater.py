import os
import ftplib
import socket
import ssl
import time
import profiler
import forge
import colorama
import getpass
import shutil
from colorama import Fore, Style
from tqdm import tqdm

print(r"==================================================================")
print(r"   _____ _ ____        _     _              _                     ")
print(r"  | ____| / ___| _ __ (_) __| | ___ _ __   | |_   _  __ _ _ __    ")
print(r"  |  _| | \___ \| '_ \| |/ _` |/ _ \ '__|  | | | | |/ _` | '_ \   ")
print(r"  | |___| |___) | |_) | | (_| |  __/ | | |_| | |_| | (_| | | | |  ")
print(r"  |_____|_|____/| .__/|_|\__,_|\___|_|  \___/ \__,_|\__,_|_| |_|  ")
print(r"        _   _ __|_| ____    _  _____ _____ ____                   ")
print(r"       | | | |  _ \|  _ \  / \|_   _| ____|  _ \                  ")
print(r"       | | | | |_) | | | |/ _ \ | | |  _| | |_) |                 ")
print(r"       | |_| |  __/| |_| / ___ \| | | |___|  _ <                  ")
print(r"        \___/|_|   |____/_/   \_\_| |_____|_| \_\                 ")
print(r"                                                                  ")
print(r"                        @Divengerss                               ")
print(r"               [https://github.com/Divengerss]               v1.0 ")
print(r"==================================================================")

colorama.init()
local_dir = os.path.join(os.getenv('APPDATA'), '.mc_serv')
credentials_file = "crd"
os.makedirs(local_dir, exist_ok=True)
files_to_del = []
update = {
    "upt": 0,
    "rem": 0
}


def set_credentials():
    server = input("Enter the server address: ")
    username = input("Enter the server login: ")
    password = getpass.getpass(prompt="Enter the server password: ")
    return server, username, password


def save_credentials(server, username, password):
    with open(os.path.join(local_dir, credentials_file), 'w') as f:
        f.write(f"{server}\n{username}\n{password}")


def read_credentials():
    local_dir = os.path.join(os.getenv('APPDATA'), '.mc_serv')
    with open(os.path.join(local_dir, credentials_file), 'r') as f:
        server = f.readline().strip()
        username = f.readline().strip()
        password = f.readline().strip()
    return server, username, password


if os.path.exists(os.path.join(os.getenv('APPDATA'), '.mc_serv', credentials_file)):
    server, username, password = read_credentials()
else:
    credentials = set_credentials()
    server = credentials[0]
    username = credentials[1]
    password = credentials[2]

connected = False
while not connected:
    try:
        ftp = ftplib.FTP_TLS(server)
        ftp.login(username, password)
        ftp.prot_p()
        connected = True
        print(Fore.GREEN + "Connected!" + Style.RESET_ALL)
        save_credentials(server, username, password)
    except ftplib.error_perm:
        print(Fore.RED + "Could not connect to " + server + ". Please try again." + Style.RESET_ALL)
        credentials = set_credentials()
        server = credentials[0]
        username = credentials[1]
        password = credentials[2]
    except socket.gaierror:
        print(Fore.RED + "Could not resolve host name. Invalid server address. Please try again." + Style.RESET_ALL)
        credentials = set_credentials()
        server = credentials[0]
        username = credentials[1]
        password = credentials[2]

ignore_list = []
try:
    with open(os.path.join(local_dir + '\\ignore.txt'), 'wb') as f:
        ftp.retrbinary(f'RETR ignore.txt', f.write)
    with open(os.path.join(local_dir + '\\ignore.txt'), 'r') as f:
        ignore_list = f.read().splitlines()
except IOError:
    print('ignore.txt file not found')
except ftplib.error_perm as e:
    if str(e).startswith("550"):
        print(Fore.YELLOW + "WARN: No ignore.txt file on the server, run directory will be purged!" + Style.RESET_ALL)
    else:
        raise e


def reconnect(ftp):
    try:
        ftp.voidcmd("NOOP")
    except:
        ftp = ftplib.FTP_TLS(server)
        ftp.login(username, password)
        ftp.prot_p()
    return ftp


def delete_files():
    pbar = tqdm(files_to_del, desc="", unit='B', unit_scale=True, leave=False)
    for file in pbar:
        description = Fore.YELLOW + 'Deleting %s' % file.replace("/", '') + Style.RESET_ALL
        pbar.set_description(f"{description:<60}")
        if os.path.isdir(file):
            shutil.rmtree(file)
            update["rem"] += 1
        elif os.path.isfile(file):
            os.remove(file)
            update["rem"] += 1
    pbar.close()


def get_local_files_to_del(in_dir: str, ftp_files: list) -> list:
    try:
        files = os.listdir(in_dir.replace("/", "\\"))
        for file in files:
            if file not in ftp_files and file not in ignore_list:
                files_to_del.append(in_dir + "\\" + file)
    except:
        pass
    return files_to_del


def download_files(ftp_path, local_path, ftp, cwd=None):
    try:
        ftp_path = ftp_path.replace('\\', '/')
        ftp = reconnect(ftp)
        if cwd is not None:
            ftp.cwd(cwd)
        ftp.cwd(ftp_path)
        files = ftp.nlst()
        pbar = tqdm(files, desc="", unit='B', unit_scale=True, leave=False)
        for file in pbar:
            description = Fore.LIGHTWHITE_EX + '%s' % file + Style.RESET_ALL
            pbar.set_description(f"{description:<60}")
            ftp = reconnect(ftp)
            if file in ignore_list:
                continue
            remote_path = os.path.join(ftp_path, file)
            try:
                ftp.cwd(file)
                ftp.cwd('..')
                isdir = True
            except:
                isdir = False
            if isdir:
                cwd = ftp.pwd()
                download_files(remote_path, local_path, ftp, cwd=cwd)
                ftp = reconnect(ftp)
                ftp.cwd(cwd)
            else:
                try:
                    mtime = ftp.sendcmd(f'MDTM {file}')
                    mtime = time.strptime(mtime[4:], '%Y%m%d%H%M%S')
                except ssl.SSLEOFError:
                    ftp = reconnect(ftp)
                local_file = os.path.join(local_path, remote_path.lstrip('/'))
                if os.path.isfile(local_file):
                    local_mtime = time.localtime(os.path.getmtime(local_file))
                    if local_mtime >= mtime:
                        continue
                local_dir = os.path.dirname(local_file)
                os.makedirs(local_dir, exist_ok=True)
                with open(local_file, 'wb') as f:
                    ftp.retrbinary(f'RETR {file}', f.write)
                    update["upt"] += 1
                os.utime(local_file, (time.mktime(mtime), time.mktime(mtime)))
        files_to_del = get_local_files_to_del(local_path + ftp_path, files)
        try:
            ftp.quit()
        except:
            pass
        pbar.close()
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            ftp.cwd('..')
            return
        else:
            raise e
    except EOFError or ssl.SSLEOFError:
        try:
            ftp.quit()
        except:
            pass
        ftp = ftplib.FTP_TLS(server)
        ftp.login(username, password)
        ftp.prot_p()


download_files('/', local_dir, ftp)
delete_files()
print(Fore.GREEN + "Complete!" + Style.RESET_ALL)
forge.get_forge()
profiler.create_profile()
print("%i files updated" % update["upt"])
print("%i files removed" % update["rem"])
print()

input(Fore.GREEN + "Done! Press enter to exit" + Style.RESET_ALL)
