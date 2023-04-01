import os

def get_forge():
    forge_version = '1.12.2-forge-14.23.5.2855'
    forge_install_dir = os.path.join(os.getenv('APPDATA'), '.minecraft', 'versions', forge_version)
    print("Checking for Forge " + forge_version + " installation...")
    if os.path.exists(forge_install_dir):
        print(f"Forge version {forge_version} is already installed.")
    else:
        print("Unable to find Forge " + forge_version)
        os.system('java -jar lib/forge-1.12.2-14.23.5.2855-installer.jar')
