"""
Module providing the CloudFlare class for interacting with the Cloudflare API.

This module contains the CloudFlare class, which is responsible for retrieving
the IPv4 and IPv6 addresses from the Cloudflare API.
"""

from requests import request, HTTPError


class CloudFlare:
    """
    Class representing the CloudFlare API.

    This class is responsible for retrieving the IPv4 and IPv6 addresses from
    the Cloudflare API.
    """

    BASE_ENDPOINT = "https://api.cloudflare.com/client/v4/"

    def get_ips(self) -> tuple[list[str], list[str], str]:
        """
        Retrieves the IPv4 and IPv6 addresses from the Cloudflare API.

        Returns:
            tuple[list[str], list[str], str]: A tuple containing three elements:
                - A list of IPv4 addresses as strings.
                - A list of IPv6 addresses as strings.
                - The ETag of the response as a string.

        Raises:
            HTTPError: If the request fails or the response status code is not 200.

        Example:
            >>> cloudflare = CloudFlare()
            >>> ips_v4, ips_v6, etag = cloudflare.get_ips()
            >>> print(ips_v4)
            ['192.0.2.1', '192.0.2.2']
            >>> print(ips_v6)
            ['2001:db8::1', '2001:db8::2']
            >>> print(etag)
            'abc123'
        """
        headers = {"Content-Type": "application/json"}

        response = request(
            "GET", f"{self.BASE_ENDPOINT}ips", headers=headers, timeout=30)

        if not response.ok or response.status_code != 200:
            raise HTTPError(
                f"Request failed with status code {response.status_code}"
                f" and message {response.text}"
            )

        data: dict = response.json()

        if not data.get("success"):
            raise HTTPError(f"Request failed with errors {data.get('errors')}")

        result: dict = data.get("result")

        etag: str = result.get("etag")
        ips_v4: list[str] = result.get("ipv4_cidrs", [])
        ips_v6: list[str] = result.get("ipv6_cidrs", [])

        return ips_v4, ips_v6, etag
