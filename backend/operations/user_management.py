import pexpect
import re
import os

from backend.logger import logger


script_path = "/root/openvpn-install.sh"


def create_user_on_server(name, expiry_date) -> bool:
    try:
        if not os.path.exists(script_path):
            logger.error("script not found on ")
            return False

        env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
        bash = pexpect.spawn(
            "/usr/bin/bash",
            [script_path],
            env=env,
            encoding="utf-8",
            timeout=120,
        )

        bash.expect(r"Option:", timeout=90)
        bash.sendline("1")

        bash.expect(r"Name:", timeout=90)
        bash.sendline(name)
        bash.expect(pexpect.EOF, timeout=180)

        bash.close()
        return True

    except pexpect.TIMEOUT:
        logger.error("Timeout occurred while executing script!")
        return False
    except pexpect.EOF:
        logger.error("Script closed earlier than expected!")
        return False
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return False


async def delete_user_on_server(name) -> bool | str:
    try:
        if not os.path.exists(script_path):
            logger.error("script not found on ")
            return False

        env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
        bash = pexpect.spawn(
            "/usr/bin/bash",
            [script_path],
            env=env,
            encoding="utf-8",
            timeout=120,
        )

        bash = pexpect.spawn(f"bash {script_path}", encoding="utf-8", timeout=60)

        bash.expect("Option:")
        bash.sendline("2")

        bash.expect("Client:")
        list_output = bash.before

        pattern = re.compile(r"\s*(\d+)\)\s*(.+)")
        matches = pattern.findall(list_output)

        user_number = None
        for num, user in matches:
            if user.strip() == name:
                user_number = num
                break

        if not user_number:
            logger.error(f"User '{name}' not found for delete!")
            bash.close()
            return "not_found"

        bash.sendline(user_number)

        bash.expect(r"\[y/N\]:", timeout=30)
        bash.sendline("y")

        bash.expect(pexpect.EOF)
        file_to_delete = f"/root/{name}.ovpn"
        if os.path.exists(file_to_delete):
            try:
                os.remove(file_to_delete)
                return True
            except Exception as e:
                logger.error(f"Error deleting file {file_to_delete}: {e}")
                return False
        else:
            logger.warning(f"File {file_to_delete} does not exist.")
    except Exception as e:
        logger.error("Error in delete_user_on_server:", e)
        return False


def download_ovpn_file(name: str) -> str | None:
    """This function returns the path of the ovpn file for downloading"""
    file_path = f"/root/{name}.ovpn"
    if os.path.exists(file_path):
        return file_path
    else:
        logger.error(f"File {file_path} does not exist.")
        return None
