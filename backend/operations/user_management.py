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


def delete_user_on_server(name) -> bool | str:
    try:
        if not os.path.exists(script_path):
            logger.error("script not found at %s", script_path)
            return False

        env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
        bash = pexpect.spawn(
            "/usr/bin/bash", [script_path], env=env, encoding="utf-8", timeout=120
        )

        try:
            bash.expect(r"Option:|Select an option:", timeout=20)
        except pexpect.TIMEOUT:
            logger.warning("Did not see main menu prompt, attempting to continue")

        bash.sendline("2")

        try:
            bash.expect(
                r"Select the client to revoke:|Select the client to revoke", timeout=20
            )
        except pexpect.TIMEOUT:
            logger.info("Didn't match full header")

        bash.expect(r"Client:", timeout=20)
        list_output = bash.before

        pattern = re.compile(r"\s*(\d+)\)\s*(.+)")
        matches = pattern.findall(list_output)

        user_number = None
        for num, user in matches:
            if user.strip() == name:
                user_number = num
                break

        if not user_number:
            logger.error("User '%s' not found for delete!", name)
            bash.close(force=True)
            return "not_found"

        logger.info("Revoking user '%s' -> number %s", name, user_number)
        bash.sendline(user_number)

        try:
            bash.expect(
                r"Confirm .*revocation\?.*\[y/N\]:|Confirm .*revocation\?.*:|Confirm .*revocation\?",
                timeout=20,
            )
            bash.sendline("y")
        except pexpect.TIMEOUT:
            logger.warning("Confirmation prompt not seen; trying to continue")

        bash.expect(pexpect.EOF, timeout=120)
        bash.close()

        # remove local .ovpn file if exists
        file_to_delete = f"/root/{name}.ovpn"
        if os.path.exists(file_to_delete):
            try:
                os.remove(file_to_delete)
                logger.info("Removed %s", file_to_delete)
            except Exception as e:
                logger.error("Error deleting file %s: %s", file_to_delete, e)
                return True

        return True

    except Exception as e:
        logger.exception("Error in delete_user_on_server: %s", e)
        return False


def download_ovpn_file(name: str) -> str | None:
    """This function returns the path of the ovpn file for downloading"""
    file_path = f"/root/{name}.ovpn"
    if os.path.exists(file_path):
        return file_path
    else:
        logger.error(f"File {file_path} does not exist.")
        return None
