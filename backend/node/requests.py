import requests
from fastapi.responses import Response
from backend.logger import logger
import time
from typing import Optional, Tuple


class NodeRequests:
    """Handles requests to the node API with timeout and retry logic."""

    def __init__(
        self,
        address: str,
        port: int,
        api_key: str,
        tunnel_addres: str = "ovpanel.com",
        protocol: str = "tcp",
        ovpn_port: int = 1194,
        set_new_setting: bool = False,
        timeout: int = 10,  # Default timeout 10 seconds
        max_retries: int = 2,  # Default 2 retries
    ):
        self.address = f"{address}:{port}"
        self.headers = {"key": api_key}
        self.tunnel_addres = tunnel_addres
        self.protocol = protocol
        self.ovpn_port = ovpn_port
        self.set_new_setting = set_new_setting
        self.timeout = timeout
        self.max_retries = max_retries

    def _make_request(
        self, method: str, url: str, **kwargs
    ) -> Tuple[Optional[requests.Response], Optional[float]]:
        """Make HTTP request with timeout and retry logic.
        
        Returns:
            Tuple of (response, response_time_in_seconds)
        """
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                if "timeout" not in kwargs:
                    kwargs["timeout"] = self.timeout
                
                if method.upper() == "GET":
                    response = requests.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response_time = time.time() - start_time
                response.raise_for_status()
                
                return response, response_time
                
            except requests.exceptions.Timeout as e:
                logger.warning(
                    f"Timeout on {url} (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                if attempt == self.max_retries:
                    logger.error(f"Max retries reached for {url}")
                    return None, None
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"Connection error on {url} (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                if attempt == self.max_retries:
                    logger.error(f"Max retries reached for {url}")
                    return None, None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on {url}: {e}")
                return None, None
                
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                time.sleep(2 ** attempt)
        
        return None, None

    def check_node(self) -> Tuple[bool, Optional[float]]:
        """Checks the node status and sets new settings if necesary.
        
        Returns:
            Tuple of (is_healthy, response_time)
        """
        api = f"http://{self.address}/sync/get-status"
        data = {
            "tunnel_address": self.tunnel_addres,
            "protocol": self.protocol,
            "ovpn_port": self.ovpn_port,
            "set_new_setting": self.set_new_setting,
        }
        
        response, response_time = self._make_request(
            "POST", api, headers=self.headers, json=data
        )
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    return True, response_time
                else:
                    logger.error(f"Node {self.address} is not reachable")
                    return False, response_time
            except Exception as e:
                logger.error(f"Error parsing response from {self.address}: {e}")
                return False, response_time
        
        return False, None

    def get_node_info(self) -> dict:
        """Get detailed node information."""
        api = f"http://{self.address}/sync/get-status"
        
        response, response_time = self._make_request("GET", api, headers=self.headers)
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    data = json_data.get("data", {})
                    data["response_time"] = response_time
                    return data
                else:
                    logger.error(
                        f"Failed to get node info on {self.address}: {json_data.get('msg')}"
                    )
                    return {}
            except Exception as e:
                logger.error(f"Error parsing node info from {self.address}: {e}")
                return {}
        
        return {}

    def create_user(self, name: str) -> bool:
        """Create user on node."""
        api = f"http://{self.address}/sync/create-user"
        data = {"name": name}
        
        response, _ = self._make_request(
            "POST", api, headers=self.headers, json=data
        )
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    return True
                else:
                    logger.error(
                        f"Failed to create user on node {self.address}: {json_data.get('msg')}"
                    )
                    return False
            except Exception as e:
                logger.error(f"Error parsing create user response from {self.address}: {e}")
                return False
        
        return False

    # def update_user(self):
    #     pass

    def download_ovpn_client(self, name: str) -> Response:
        """Download OVPN client configuration."""
        api = f"http://{self.address}/sync/download/ovpn/{name}"
        
        response, _ = self._make_request("GET", api, headers=self.headers)
        
        if response and response.status_code == 200:
            return Response(
                content=response.content,
                media_type="application/x-openvpn-profile",
                headers={
                    "Content-Disposition": f"attachment; filename={name}.ovpn"
                },
            )
        
        logger.error(f"Error downloading OVPN client from node {self.address}")
        return None

    def delete_user(self, name: str) -> bool:
        """Delete user from node."""
        api = f"http://{self.address}/sync/delete-user"
        data = {"name": name}
        
        response, _ = self._make_request(
            "POST", api, headers=self.headers, json=data
        )
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    return True
                else:
                    logger.error(
                        f"Failed to delete user on node {self.address}: {json_data.get('msg')}"
                    )
                    return False
            except Exception as e:
                logger.error(f"Error parsing delete user response from {self.address}: {e}")
                return False
        
        return False

    def get_all_users(self) -> list:
        """Get all users from node."""
        api = f"http://{self.address}/sync/users"
        
        response, _ = self._make_request("GET", api, headers=self.headers)
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    return json_data.get("data", [])
                else:
                    logger.error(
                        f"Failed to get users from node {self.address}: {json_data.get('msg')}"
                    )
                    return []
            except Exception as e:
                logger.error(f"Error parsing users from {self.address}: {e}")
                return []
        
        return []
