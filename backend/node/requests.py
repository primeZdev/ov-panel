import requests
from fastapi.responses import Response
from backend.logger import logger


class NodeRequests:
    """Handles requests to the node API."""

    def __init__(
        self,
        address: str,
        port: int,
        api_key: str,
        tunnel_addres: str = "ovpanel.com",
        protocol: str = "tcp",
        ovpn_port: int = 1194,
        set_new_setting: bool = False,
    ):
        self.address = f"{address}:{port}"
        self.headers = {"key": api_key}
        self.tunnel_addres = tunnel_addres
        self.protocol = protocol
        self.ovpn_port = ovpn_port
        self.set_new_setting = set_new_setting

    def check_node(self) -> bool:
        """Checks the node status and sets new settings if necesary."""
        api = f"http://{self.address}/sync/get-status"
        try:
            data = {
                "tunnel_address": self.tunnel_addres,
                "protocol": self.protocol,
                "ovpn_port": self.ovpn_port,
                "set_new_setting": self.set_new_setting,
            }
            response = requests.post(api, headers=self.headers, json=data).json()
            if response.get("success"):
                return True
            else:
                logger.error(f"Node {self.address} is not reachable")
                return False
        except Exception as e:
            logger.error(f"Error checking node {self.address}: {e}")
            return False

    def get_node_info(self) -> dict:
        api = f"http://{self.address}/sync/get-status"
        try:
            response = requests.get(api, headers=self.headers).json()
            if response.get("success"):
                return response.get("data")
            else:
                logger.error(f"Failed to get node info on {self.address}: {response.get('msg')}")
                return {}
        except Exception as e:
            logger.error(f"Error getting node info on {self.address}: {e}")
            return {}

    def create_user(self, name: str) -> bool:
        api = f"http://{self.address}/sync/create-user"
        data = {"name": name}
        try:
            response = requests.post(api, headers=self.headers, json=data).json()
            if response.get("success"):
                return True
            else:
                logger.error(f"Failed to create user on node {self.address}: {response.get('msg')}")
                return False
        except Exception as e:
            logger.error(f"Error creating user on node {self.address}: {e}")
            return False

    # def update_user(self):
    #     pass

    def download_ovpn_client(self, name: str) -> Response:
        api = f"http://{self.address}/sync/download/ovpn/{name}"
        try:
            response = requests.get(api, headers=self.headers)
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/x-openvpn-profile",
                    headers={"Content-Disposition": f"attachment; filename={name}.ovpn"},
                )
        except Exception as e:
            logger.error(f"Error downloading OVPN client from node {self.address}: {e}")
        return None

    def delete_user(self, name: str) -> bool:
        api = f"http://{self.address}/sync/delete-user"
        data = {"name": name}
        try:
            response = requests.post(api, headers=self.headers, json=data).json()
            if response.get("success"):
                return True
            else:
                logger.error(f"Failed to delete user on node {self.address}: {response.get('msg')}")
                return False
        except Exception as e:
            logger.error(f"Error deleting user on node {self.address}: {e}")
            return False
