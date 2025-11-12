import requests
from fastapi.responses import Response
from backend.logger import logger
import time
from typing import Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial


# Thread pool for async operations
_executor = ThreadPoolExecutor(max_workers=10)


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
        timeout: int = 5,  # Reduced to 5 seconds
        max_retries: int = 1,  # Reduced to 1 retry
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
        # Always set timeout
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                if method.upper() == "GET":
                    response = requests.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response_time = time.time() - start_time
                response.raise_for_status()
                
                return response, response_time
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                error_type = "Timeout" if isinstance(e, requests.exceptions.Timeout) else "Connection error"
                if attempt == self.max_retries:
                    logger.warning(f"{error_type} on {url} after {attempt + 1} attempts")
                    return None, None
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error on {url}: {str(e)[:100]}")
                return None, None
        
        return None, None
    
    async def _make_request_async(
        self, method: str, url: str, **kwargs
    ) -> Tuple[Optional[requests.Response], Optional[float]]:
        """Async wrapper for _make_request using thread pool."""
        loop = asyncio.get_event_loop()
        func = partial(self._make_request, method, url, **kwargs)
        return await loop.run_in_executor(_executor, func)

    def check_node(self) -> Tuple[bool, Optional[float]]:
        """Checks the node status and sets new settings if necessary.
        
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
            except Exception:
                pass
        
        return False, None
    
    async def check_node_async(self) -> Tuple[bool, Optional[float]]:
        """Async version of check_node."""
        api = f"http://{self.address}/sync/get-status"
        data = {
            "tunnel_address": self.tunnel_addres,
            "protocol": self.protocol,
            "ovpn_port": self.ovpn_port,
            "set_new_setting": self.set_new_setting,
        }
        
        response, response_time = await self._make_request_async(
            "POST", api, headers=self.headers, json=data
        )
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    return True, response_time
            except Exception:
                pass
        
        return False, None

    async def get_node_info_async(self) -> dict:
        """Async version to get detailed node information including CPU and memory."""
        api = f"http://{self.address}/sync/get-status"
        data = {
            "tunnel_address": self.tunnel_addres,
            "protocol": self.protocol,
            "ovpn_port": self.ovpn_port,
            "set_new_setting": self.set_new_setting,
        }
        
        response, response_time = await self._make_request_async(
            "POST", api, headers=self.headers, json=data
        )
        
        if response and response.status_code == 200:
            try:
                json_data = response.json()
                if json_data.get("success"):
                    node_data = json_data.get("data", {})
                    node_data["response_time"] = response_time
                    return node_data
            except Exception:
                pass
        
        return {}

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
            except Exception:
                pass
        
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
