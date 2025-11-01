import os
import requests
import sys
import pexpect
import subprocess
import shutil
from colorama import Fore, Style


def install_ovpanel():
    try:
        subprocess.run(
            ["wget", "https://git.io/vpn", "-O", "/root/openvpn-install.sh"], check=True
        )  # thanks to Nyr for ovpn installation script <3 https://github.com/Nyr/openvpn-install

        bash = pexpect.spawn("bash /root/openvpn-install.sh", encoding="utf-8", timeout=60)
        subprocess.run("clear")
        print("Please wait while the prerequisites are installed...")

        bash.expect("Which IPv4 address should be used")
        bash.sendline("1")

        bash.expect("Which protocol should OpenVPN use")
        bash.sendline("2")

        bash.expect("What port should OpenVPN listen on")
        bash.sendline("1194")

        bash.expect("Select a DNS server for the clients")
        bash.sendline("1")

        bash.expect("Enter a name for the first client")
        bash.sendline("first_client")

        bash.expect("Press any key to continue")
        bash.sendline("")

        bash.expect("Finished!")
        subprocess.run("clear")
        shutil.copy(".env.example", ".env")

        panel_username = input("OVPanel username: ")
        panel_password = input("OVPanel password: ")
        panel_port = input("OVPanel port number: ")
        panel_path = input("OVPanel path: ")

        replacements = {
            "ADMIN_USERNAME": panel_username,
            "ADMIN_PASSWORD": panel_password,
            "PORT": panel_port,
            "URLPATH": panel_path,
        }

        lines = []
        with open(".env", "r") as f:
            for line in f:
                for key, value in replacements.items():
                    if line.startswith(f"{key}="):
                        line = f"{key}={value}\n"
                lines.append(line)

        with open(".env", "w") as f:
            f.writelines(lines)

        subprocess.run(["uv", "sync"], check=True)
        migrate()

        print(
            Fore.GREEN
            + f"OV-Panel installation completed successfully!\nYou can now access the panel at: http://your-server-ip:{panel_port}/{panel_path}"
            + Style.RESET_ALL
        )
        run_ovpanel()
        input("Press Enter to return to the menu...")
        menu()

    except Exception as e:
        print(Fore.RED + "Error occurred during installation: " + str(e) + Style.RESET_ALL)
        input("Press Enter to return to the menu...")
        menu()


def update_ovpanel():
    print(Fore.YELLOW + "Updating OV-Panel, please wait..." + Style.RESET_ALL)
    try:
        repo = "https://api.github.com/repos/primeZdev/ov-panel/releases/latest"
        install_dir = "/opt/ov-panel"
        env_file = os.path.join(install_dir, ".env")
        data_dir = os.path.join(install_dir, "data")
        backup_env = "/tmp/ovpanel_env_backup"
        backup_data = "/tmp/ovpanel_data_backup"

        response = requests.get(repo)
        response.raise_for_status()
        release = response.json()
        download_url = release["tarball_url"]
        filename = "/tmp/ov-panel-latest.tar.gz"

        print(Fore.YELLOW + f"Downloading {download_url}" + Style.RESET_ALL)
        subprocess.run(["wget", "-O", filename, download_url], check=True)

        if os.path.exists(env_file):
            shutil.copy2(env_file, backup_env)
        if os.path.exists(data_dir):
            shutil.copytree(data_dir, backup_data, dirs_exist_ok=True)

        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)

        os.makedirs(install_dir, exist_ok=True)
        subprocess.run(
            ["tar", "-xzf", filename, "-C", install_dir, "--strip-components=1"],
            check=True,
        )

        if os.path.exists(backup_env):
            shutil.move(backup_env, env_file)
        if os.path.exists(backup_data):
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
            shutil.move(backup_data, data_dir)

        os.chdir(install_dir)
        # Install dependencies using uv sync with refresh to update lock file
        subprocess.run(["uv", "sync", "--refresh"], check=True)
        migrate()

        subprocess.run(["systemctl", "restart", "ov-panel"], check=True)

        print(Fore.GREEN + "OV-Panel updated successfully!" + Style.RESET_ALL)
        input("Press Enter to return to the menu...")
        menu()

    except Exception as e:
        print(Fore.RED + f"Update failed: {str(e)}" + Style.RESET_ALL)
        input("Press Enter to return to the menu...")
        menu()


def uninstall_ovpanel():
    try:
        uninstall = input("Do you want to uninstall OV-Panel? (y/n): ")
        if uninstall.lower() != "y":
            print("Uninstallation canceled.")
            menu()

        bash = pexpect.spawn("bash /root/openvpn-install.sh", timeout=60)
        subprocess.run("clear")
        print("Please wait...")

        bash.expect("Option:")
        bash.sendline("3")

        bash.expect("Confirm OpenVPN removal")
        bash.sendline("y")

        bash.expect("OpenVPN removed!")
        os.remove("/etc/systemd/system/ov-panel.service")
        print(Fore.GREEN + "OV-Panel uninstallation completed successfully!" + Style.RESET_ALL)
        deactivate_ovpanel()
        input("Press Enter to return to the menu...")
        menu()

    except Exception as e:
        print(Fore.RED + "Error occurred during uninstallation: " + str(e) + Style.RESET_ALL)
        input("Press Enter to return to the menu...")
        menu()


def migrate() -> None:
    """Migrate the database to the latest version"""
    backend_dir = "/opt/ov-panel/backend"
    current_dir = os.getcwd()

    try:
        os.chdir(backend_dir)
        if not os.path.exists("alembic.ini"):
            return

        print(Fore.YELLOW + "Running Alembic migration..." + Style.RESET_ALL)
        subprocess.run(["alembic", "upgrade", "head"], check=True)

        print(Fore.GREEN + "Database migrated successfully!" + Style.RESET_ALL)

    except subprocess.CalledProcessError:
        print(Fore.RED + "Database migration failed!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {e}" + Style.RESET_ALL)
    finally:
        os.chdir(current_dir)


def run_ovpanel() -> None:
    """Create and run a systemd service for OV-Panel"""
    service_content = """
[Unit]
Description=OV-Panel App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/ov-panel/
ExecStart=/usr/local/bin/uv run main.py
Restart=always
RestartSec=5
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
"""

    with open("/etc/systemd/system/ov-panel.service", "w") as f:
        f.write(service_content)

    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "enable", "ov-panel"])
    subprocess.run(["sudo", "systemctl", "start", "ov-panel"])


def deactivate_ovpanel() -> None:
    """Stop and disable the OV-Panel systemd service"""
    subprocess.run(["sudo", "systemctl", "stop", "ov-panel"])
    subprocess.run(["sudo", "systemctl", "disable", "ov-panel"])
    subprocess.run(["rm", "-f", "/etc/systemd/system/ov-panel.service"])


def menu():
    subprocess.run("clear")
    print(Fore.GREEN + "=" * 34)
    print("Welcome to the OV-Panel Installer")
    print("=" * 34 + Style.RESET_ALL)
    print()
    print("Please choose an option:\n")
    print("  1. Install")
    print("  2. Update")
    print("  3. Uninstall")
    print("  4. Exit")
    print()
    choice = input(Fore.YELLOW + "Enter your choice: " + Style.RESET_ALL)

    if choice == "1":
        install_ovpanel()
    elif choice == "2":
        update_ovpanel()
    elif choice == "3":
        uninstall_ovpanel()
    elif choice == "4":
        print(Fore.GREEN + "\nExiting... Goodbye!" + Style.RESET_ALL)
        sys.exit()
    else:
        print(Fore.RED + "\nInvalid choice. Please try again." + Style.RESET_ALL)
        input(Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
        menu()


if __name__ == "__main__":
    menu()
