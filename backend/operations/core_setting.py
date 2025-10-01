import pexpect
import re

from logger import logger
from schema._input import SettingsUpdate


def change_config(request: SettingsUpdate) -> bool:
    setting_file = "/etc/openvpn/server/server.conf"
    template_file = "/etc/openvpn/server/client-common.txt"
    try:
        with open(setting_file, "r") as file:
            config = file.read()
        config = re.sub(
            r"^port\s+\d+", f"port {request.port}", config, flags=re.MULTILINE
        )
        config = re.sub(
            r"^proto\s+\w+",
            f"proto {request.protocol}",
            config,
            flags=re.MULTILINE,
        )
        config = re.sub(
            r"^local\s+.*",
            f"local {request.tunnel_address}",
            config,
            flags=re.MULTILINE,
        )

        with open(setting_file, "w") as file:
            file.write(config)

        # Update the client template
        with open(template_file, "r") as file:
            template = file.read()
        template = re.sub(
            r"^remote\s+\S+\s+\d+",
            f"remote {request.tunnel_address} {request.port}",
            template,
            flags=re.MULTILINE,
        )
        template = re.sub(
            r"^proto\s+\w+",
            f"proto {request.protocol}",
            template,
            flags=re.MULTILINE,
        )
        with open(template_file, "w") as file:
            file.write(template)

        restart_openvpn()
        logger.info(
            f"OpenVPN port changed to {request.port}, protocol to {request.protocol}, and tunnel address to {request.tunnel_address}"
        )
        return True
    except Exception as e:
        logger.error(f"Error changing OpenVPN settings: {e}")
        return False


def restart_openvpn() -> None:
    """Restart the OpenVPN service with systemctl"""
    try:
        logger.info("Restarting OpenVPN service...")
        # Use pexpect to restart the OpenVPN service
        child = pexpect.spawn(
            "systemctl restart openvpn-server@server", encoding="utf-8"
        )
        child.expect(pexpect.EOF)
        logger.info("OpenVPN service restarted successfully.")
    except Exception as e:
        logger.error(f"Error restarting OpenVPN service: {e}")
