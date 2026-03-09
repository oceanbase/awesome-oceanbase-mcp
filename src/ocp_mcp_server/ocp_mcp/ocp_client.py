"""OCP API client with AK/SK signature authentication.

Signature rules per OCP doc: toSignString = HttpMethod + "\\n" + Md5Payload + "\\n"
+ ContentType + "\\n" + RequestDate + "\\n" + Host + "\\n" + OCP-Headers + "\\n"
+ PathAndQueryParams. Sign with BASE64(HMAC-SHA1(AccessKeySecret, string-to-sign)).
"""

import base64
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


class OCPClient:
    """OCP API client with AK/SK signature authentication."""

    def __init__(
        self,
        host: str,
        access_key_id: str,
        access_key_secret: str,
        timeout: int = 30,
    ):
        """
        Initialize OCP client.

        Args:
            host: OCP server host (e.g. "127.0.0.1:8080" or "http://xxx:8080")
            access_key_id: Access key ID (AK)
            access_key_secret: Access key secret (SK)
            timeout: Request timeout in seconds
        """
        if not host:
            raise ValueError("host parameter is required and cannot be None or empty")
        if not access_key_id:
            raise ValueError(
                "access_key_id parameter is required and cannot be None or empty"
            )
        if not access_key_secret:
            raise ValueError(
                "access_key_secret parameter is required and cannot be None or empty"
            )

        raw = host.strip()
        if raw.startswith("http://"):
            raw = raw[7:]
        elif raw.startswith("https://"):
            raw = raw[8:]
        self.host = raw.rstrip("/")
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.base_url = f"http://{self.host}"
        self.client = httpx.Client(timeout=timeout)

    def _get_rfc_date(self) -> str:
        """Get RFC 1123 formatted date string."""
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _md5_hash(self, data: bytes) -> str:
        """Calculate MD5 hash of data."""
        if not data:
            return ""
        md5_hash = hashlib.md5(data).hexdigest().upper()
        return md5_hash.zfill(32)

    def _hmac_sha1(self, key: str, data: bytes) -> bytes:
        """Calculate HMAC-SHA1 signature."""
        return hmac.new(key.encode("utf-8"), data, hashlib.sha1).digest()

    def _get_signature(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        rfc_date: Optional[str] = None,
    ) -> str:
        """
        Generate OCP API signature.

        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            params: Query parameters
            body: Request body
            rfc_date: RFC date string

        Returns:
            Base64 encoded signature
        """
        if rfc_date is None:
            rfc_date = self._get_rfc_date()

        if headers is None:
            headers = {}

        # Build string to sign
        str_to_sign_parts = []

        # 1. HTTP method
        str_to_sign_parts.append(method.upper())

        # 2. Content MD5 (payload)
        if body is None:
            str_to_sign_parts.append("")
        else:
            str_to_sign_parts.append(self._md5_hash(body))

        # 3. Content-Type
        content_type = headers.get("Content-Type", "")
        str_to_sign_parts.append(content_type)

        # 4. Date
        str_to_sign_parts.append(rfc_date)

        # 5. Host
        str_to_sign_parts.append(self.host)

        # 6. OCP headers (x-ocp-*)
        ocp_headers = {
            k: v for k, v in headers.items() if k.lower().startswith("x-ocp-")
        }
        if ocp_headers:
            ocp_header_str = "\n".join(
                f"{k}:{v}" for k, v in sorted(ocp_headers.items())
            )
            str_to_sign_parts.append(ocp_header_str)
        else:
            str_to_sign_parts.append("")

        # 7. Path and query parameters
        if params:
            # Sort parameters and URL encode
            sorted_params = sorted(params.items())
            encoded_params = []
            for key, value in sorted_params:
                encoded_key = quote(str(key), safe="")
                encoded_value = quote(str(value), safe="")
                encoded_params.append(f"{encoded_key}={encoded_value}")

            query_string = "&".join(encoded_params)
            str_to_sign_parts.append(f"{path}?{query_string}")
        else:
            str_to_sign_parts.append(path)

        # Join with newlines
        str_to_sign = "\n".join(str_to_sign_parts)

        logger.debug(f"String to sign: {repr(str_to_sign)}")

        # Calculate signature
        signature_bytes = self._hmac_sha1(
            self.access_key_secret, str_to_sign.encode("utf-8")
        )

        return base64.b64encode(signature_bytes).decode("utf-8")

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        return_binary: bool = False,
    ) -> Union[Dict[str, Any], bytes]:
        """
        Make authenticated request to OCP API.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters
            json: JSON body
            headers: Additional headers
            return_binary: If True, return binary content instead of JSON

        Returns:
            Response JSON data or binary content
        """
        if headers is None:
            headers = {}

        headers.setdefault("Content-Type", "application/json")

        headers["x-ocp-origin"] = "mcp-server"

        # Prepare body
        body = None
        if json is not None:
            import json as json_module

            body = json_module.dumps(json).encode("utf-8")

        # Generate RFC date
        rfc_date = self._get_rfc_date()

        # Generate signature
        signature = self._get_signature(
            method=method,
            path=path,
            headers=headers,
            params=params,
            body=body,
            rfc_date=rfc_date,
        )

        # Add authentication headers
        headers["Authorization"] = (
            f"OCP-ACCESS-KEY-HMACSHA1 {self.access_key_id}:{signature}"
        )
        headers["Date"] = rfc_date

        # Make request
        if params:
            sorted_params = sorted(params.items())
            encoded = [
                f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
                for k, v in sorted_params
            ]
            url = f"{self.base_url}{path}?{'&'.join(encoded)}"
            request_params = None
        else:
            url = f"{self.base_url}{path}"
            request_params = None

        logger.debug(
            f"Making {method} request to {url}" + (" (binary)" if return_binary else "")
        )
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Params: {params}")

        response = self.client.request(
            method=method,
            url=url,
            params=request_params,
            content=body,
            headers=headers,
        )

        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")

        response.raise_for_status()

        if return_binary:
            return response.content
        else:
            return response.json()

    def get(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request(
            "POST", path, params=params, json=json, headers=headers
        )

    def put(
        self,
        path: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request(
            "PUT", path, params=params, json=json, headers=headers
        )

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", path, params=params, headers=headers)

    def get_binary(
        self,
        path: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """
        Make GET request and return binary content.

        Args:
            path: Request path
            params: Query parameters
            headers: Additional headers

        Returns:
            Response binary content
        """
        result = self._make_request(
            method="GET",
            path=path,
            params=params,
            headers=headers,
            return_binary=True,
        )
        return result  # type: ignore

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
