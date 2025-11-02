import os
import requests
import pexpect
import sys
import subprocess
import shutil
import secrets
import base64
import getpass
import time
from colorama import Fore, Style, init

init(autoreset=True)


def create_secret_key(length: int = 64) -> str:
    random_bytes = secrets.token_bytes(length)
    secret_key = base64.b64encode(random_bytes).decode("utf-8").rstrip("=")
    return secret_key


def get_server_ip():
    try:
        result = subprocess.run(
            ["hostname", "-I"], capture_output=True, text=True, check=True
        )
        ip_addresses = result.stdout.strip().split()
        return ip_addresses[0] if ip_addresses else "your-server-ip"
    except:
        return "your-server-ip"


def display_panel_info(username, password, port, path):
    subprocess.run("clear")
    server_ip = get_server_ip()
    url = f"http://{server_ip}:{port}/{path}" if path else f"http://{server_ip}:{port}/"

    print(f"\n{Fore.CYAN}Access URL: {url}{Style.RESET_ALL}\n")


def ask_user(prompt, allow_empty=False, input_type="text"):
    while True:
        try:
            if input_type == "password":
                value = getpass.getpass(prompt)
            else:
                value = input(prompt)

            if not allow_empty and not value.strip():
                print(Fore.RED + "Input cannot be empty. Please try again...")
                time.sleep(2)
                subprocess.run("clear")
                continue
            if input_type == "port":
                try:
                    port_num = int(value)
                    if not (1 <= port_num <= 65535):
                        print(Fore.RED + "Port must be between 1 and 65535.")
                        time.sleep(2)
                        subprocess.run("clear")
                        continue
                except ValueError:
                    print(Fore.RED + "Port must be a valid number.")
                    time.sleep(2)
                    subprocess.run("clear")
                    continue
            return value.strip()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)


def ask_password(prompt):
    while True:
        try:
            password = getpass.getpass(prompt)
            if not password.strip():
                print(Fore.RED + "Password cannot be empty. Please try again...")
                time.sleep(2)
                subprocess.run("clear")
                continue
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print(Fore.RED + "Passwords do not match. Please try again...")
                time.sleep(2)
                subprocess.run("clear")
                continue
            return password
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)


def show_banner():
    subprocess.run("clear")
    banner = f"""
{Fore.CYAN} ____  _     ____  ____  _      _____ _    
/  _ \\/ \\ |\\/  __\\/  _ \\/ \\  /|/  __// \\   
| / \\|| | //|  \\/|| / \\|| |\\ |||  \\  | |   
| \\_/|| \\// |  __/| |-||| | \\|||  /_ | |_/\\\\
\\____/\\__/  \\_/   \\_/ \\|\\_/  \\|\\____\\\\____/
{Style.RESET_ALL}
"""
    print(banner)


def show_menu():
    show_banner()

    print(f"{Fore.YELLOW}Please choose an option:{Style.RESET_ALL}\n")

    options = [
        ("1", "Install", Fore.GREEN),
        ("2", "Update", Fore.CYAN),
        ("3", "Uninstall", Fore.RED),
        ("4", "Exit", Fore.YELLOW),
    ]

    for num, desc, color in options:
        print(f"  {color}[{num}]{Style.RESET_ALL} {desc}")

    print()


def ask_choice():
    while True:
        try:
            choice = input(f"{Fore.YELLOW}Enter your choice: {Style.RESET_ALL}")

            if choice in ["1", "2", "3", "4"]:
                return choice
            else:
                print(
                    f"\n{Fore.RED}Invalid choice. Please enter a number between 1-4{Style.RESET_ALL}"
                )
                time.sleep(2)
                show_menu()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)


def ask_confirmation(prompt):
    while True:
        try:
            choice = input(f"{Fore.YELLOW}{prompt} {Style.RESET_ALL}").strip().lower()
            if choice in ["y", "yes", "n", "no"]:
                return choice in ["y", "yes"]
            else:
                print(Fore.RED + "Please enter 'y' for yes or 'n' for no")
                time.sleep(2)
                subprocess.run("clear")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)


def setup_panel():
    try:
        subprocess.run("clear")
        print(f"\n{Fore.YELLOW}Installing OpenVPN Core...{Style.RESET_ALL}\n")

        subprocess.run(
            ["wget", "https://git.io/vpn", "-O", "/root/openvpn-install.sh"],
            check=True,  # thanks to Nyr for ovpn installation script <3 https://github.com/Nyr/openvpn-install
        )

        bash = pexpect.spawn(
            "/usr/bin/bash", ["/root/openvpn-install.sh"], encoding="utf-8", timeout=180
        )

        prompts = [
            (r"Which IPv4 address should be used.*:", "1"),
            (r"Protocol.*:", "2"),
            (r"Port.*:", "1194"),
            (r"Select a DNS server for the clients.*:", "1"),
            (r"Enter a name for the first client.*:", "first_client"),
            (r"Press any key to continue...", ""),
        ]

        for pattern, reply in prompts:
            try:
                bash.expect(pattern, timeout=10)
                bash.sendline(reply)
            except pexpect.TIMEOUT:
                pass

        bash.expect(pexpect.EOF, timeout=None)
        bash.close()

        shutil.copy(".env.example", ".env")

        subprocess.run("clear")
        print(f"\n{Fore.YELLOW}Panel Configuration{Style.RESET_ALL}\n")

        panel_username = ask_user(f"{Fore.GREEN}> Panel username: {Style.RESET_ALL}")
        panel_password = ask_password(f"{Fore.RED}> Panel password: {Style.RESET_ALL}")
        panel_port = ask_user(
            f"{Fore.GREEN}> Panel port number: {Style.RESET_ALL}", input_type="port"
        )
        panel_path = ask_user(
            f"{Fore.GREEN}> Panel path (optional): {Style.RESET_ALL}", allow_empty=True
        )

        replacements = {
            "ADMIN_USERNAME": panel_username,
            "ADMIN_PASSWORD": panel_password,
            "PORT": panel_port,
            "URLPATH": panel_path,
            "JWT_SECRET_KEY": create_secret_key(),
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
        apply_migrations()

        subprocess.run("clear")
        print(f"\n{Fore.YELLOW}Installation Complete!{Style.RESET_ALL}")

        display_panel_info(panel_username, panel_password, panel_port, panel_path)

        start_service()
        try:
            input(f"{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()

    except Exception as e:
        print(f"\n{Fore.RED}Installation failed: {e}{Style.RESET_ALL}")
        try:
            input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()


def refresh_panel():
    if not os.path.exists("/opt/ov-panel") or not os.path.exists(
        "/etc/systemd/system/ov-panel.service"
    ):
        subprocess.run("clear")
        print(
            f"\n{Fore.MAGENTA}OV-Panel is not installed on your system.{Style.RESET_ALL}"
        )
        print(
            f"{Fore.MAGENTA}Please install OV-Panel first using option 1.{Style.RESET_ALL}"
        )
        try:
            input(f"\n{Fore.MAGENTA}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()
        return

    print(f"\n{Fore.YELLOW}Updating OV-Panel...{Style.RESET_ALL}\n")

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

        print(f"{Fore.YELLOW}Downloading latest version...{Style.RESET_ALL}")
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
        subprocess.run(["uv", "sync", "--refresh"], check=True)
        apply_migrations()

        subprocess.run(["systemctl", "restart", "ov-panel"], check=True)

        print(f"\n{Fore.GREEN}Update Complete!{Style.RESET_ALL}\n")

        try:
            input(f"{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()

    except Exception as e:
        print(f"\n{Fore.RED}Update failed: {str(e)}{Style.RESET_ALL}")
        try:
            input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()


def remove_panel():
    try:
        if not os.path.exists("/etc/openvpn/server.conf") and not os.path.exists(
            "/etc/systemd/system/ov-panel.service"
        ):
            subprocess.run("clear")
            print(
                f"\n{Fore.YELLOW}OV-Panel is not installed on your system.{Style.RESET_ALL}"
            )
            try:
                input(
                    f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}"
                )
            except KeyboardInterrupt:
                print(
                    f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n"
                )
                sys.exit(0)
            main_menu()
            return

        subprocess.run("clear")
        print(f"\n{Fore.RED}Warning: This will remove all panel data!{Style.RESET_ALL}")

        if not ask_confirmation("Do you want to proceed? (y/n): "):
            print(f"\n{Fore.YELLOW}Uninstallation cancelled.{Style.RESET_ALL}")
            time.sleep(1)
            main_menu()
            return

        bash = pexpect.spawn("bash /root/openvpn-install.sh", timeout=60)
        subprocess.run("clear")
        print(f"\n{Fore.YELLOW}Processing removal...{Style.RESET_ALL}\n")

        bash.expect("Option:")
        bash.sendline("3")

        bash.expect("Confirm OpenVPN removal")
        bash.sendline("y")

        bash.expect("OpenVPN removed!")

        if os.path.exists("/etc/systemd/system/ov-panel.service"):
            os.remove("/etc/systemd/system/ov-panel.service")

        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        stop_service()

        print(f"\n{Fore.GREEN}Uninstallation Complete!{Style.RESET_ALL}\n")

        stop_service()
        try:
            input(f"{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()

    except Exception as e:
        print(f"\n{Fore.RED}Uninstallation failed: {str(e)}{Style.RESET_ALL}")
        try:
            input(f"\n{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit(0)
        main_menu()


def apply_migrations() -> None:
    backend_dir = "/opt/ov-panel/backend"
    current_dir = os.getcwd()

    try:
        os.chdir(backend_dir)
        if not os.path.exists("alembic.ini"):
            return

        print(f"{Fore.YELLOW}Running Alembic migration...{Style.RESET_ALL}")
        subprocess.run(["alembic", "upgrade", "head"], check=True)

        print(f"{Fore.GREEN}Database migrated successfully!{Style.RESET_ALL}")

    except subprocess.CalledProcessError:
        print(f"{Fore.RED}Database migration failed!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
    finally:
        os.chdir(current_dir)


def start_service() -> None:
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


def stop_service() -> None:
    service_file = "/etc/systemd/system/ov-panel.service"

    subprocess.run(["sudo", "systemctl", "stop", "ov-panel"], stderr=subprocess.DEVNULL)

    if os.path.exists(service_file):
        subprocess.run(["rm", "-f", service_file])

    subprocess.run(["sudo", "systemctl", "daemon-reload"])
    subprocess.run(["sudo", "systemctl", "reset-failed"], stderr=subprocess.DEVNULL)


def main_menu():
    try:
        show_menu()
        choice = ask_choice()

        if choice == "1":
            setup_panel()
        elif choice == "2":
            refresh_panel()
        elif choice == "3":
            remove_panel()
        elif choice == "4":
            print(f"\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
            sys.exit()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Thank you for using OV-Panel!{Style.RESET_ALL}\n")
        sys.exit(0)
