import os

def get_fabric():
    fabric_version = 'fabric-loader-0.14.19-1.19.3'
    forge_install_dir = os.path.join(os.getenv('APPDATA'), '.minecraft', 'versions', fabric_version)
    print("Checking for Fabric " + fabric_version + " installation...")
    if os.path.exists(forge_install_dir):
        print(f"Fabric version {fabric_version} is already installed.")
    else:
        print("Unable to find Fabric " + fabric_version)
        os.system('java -jar lib/fabric-installer-0.11.2.jar')
