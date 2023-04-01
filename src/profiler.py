import json
import os
import psutil
import shutil


def get_profile_icon() -> str:
    icon = "data:image/png;base64,"
    with open("ico", "r") as f:
        icon += f.read()
    return icon


def create_profile():
    total_memory = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    profile_name = "[1.12.2] El Spider Juan Server"
    version_id = "1.12.2-forge-14.23.5.2855"
    game_args = ""
    launcher_profiles_path = os.path.join(os.environ['APPDATA'], '.minecraft', 'launcher_profiles.json')

    with open(launcher_profiles_path, "r") as file:
        launcher_profiles = json.load(file)

    if profile_name not in launcher_profiles["profiles"]:
        new_profile = {
            "name": profile_name,
            "type": "custom",
            "created": "2023-03-30T00:00:00.000Z",
            "lastUsed": "2023-03-30T00:00:00.000Z",
            "icon": get_profile_icon(),
            "lastVersionId": version_id,
            "gameDir": os.path.join(os.environ['APPDATA'], '.mc_serv'),
            "javaArgs": "-Xmx" + str(round(total_memory / 1.5)) + "G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M " + game_args,
            "resolution": {
                "height": 1080,
                "width": 1920
            },
        }

        launcher_profiles["profiles"][profile_name] = new_profile

        with open(launcher_profiles_path, "w") as file:
            json.dump(launcher_profiles, file, indent=2)
            print(f"Profile '{profile_name}' added successfully to Minecraft Launcher.")
    else:
        print(f"Profile '{profile_name}' already exists in the Minecraft Launcher. Ignored.")
    server_dat = os.path.join(os.environ['APPDATA'], '.mc_serv', 'servers.dat')
    if not os.path.exists(server_dat):
        shutil.copy('servers.dat', server_dat)
        print("servers.dat copied to Minecraft run folder.")
    else:
        print("servers.dat already exists. Ignored.")
