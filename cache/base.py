from abc import ABC, abstractmethod

DEFAULT_CACHE = {
    "etag": None,
    "ips_v4": [],
    "ips_v6": []
}


class Cache(ABC):
    """
    Abstract base class for caching.
    """

    @abstractmethod
    def has(self, key: str) -> bool:
        """
        Check if the cache contains a value for the given key.

        Args:
            key (str): The key to check for.

        Returns:
            bool: True if the cache contains a value for the key, False otherwise.
        """

    @abstractmethod
    def get(self, key: str) -> str | set[str]:
        """
        Get the value associated with the given key from the cache.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            str | set[str]: The value associated with the key. If the key does not exist,
            an empty string or an empty set is returned.
        """

    @abstractmethod
    def set(self, key: str, value: str | set[str]) -> None:
        """
        Set the value associated with the given key in the cache.

        Args:
            key (str): The key to set the value for.
            value (str | set[str]): The value to set.

        Returns:
            None
        """

    def get_etag(self) -> str | None:
        """
        Get the ETag value associated with the "etag" key from the cache.

        Returns:
            str | None: The ETag value if it exists in the cache, otherwise None.
        """
        return self.get("etag") if self.has("etag") else None

    def set_etag(self, etag: str) -> None:
        """
        Set the ETag value associated with the "etag" key in the cache.

        Args:
            etag (str): The ETag value to set.

        Returns:
            None: This function does not return anything.
        """
        self.set("etag", etag)

    def get_ipv4_addresses(self) -> set[str]:
        """
        Get the list of CloudFlare IPv4 addresses from the cache.

        Returns:
            set[str]: A set of IPv4 addresses if the "ips_v4" key exists in the cache,
                      otherwise an empty set.
        """
        return self.get("ips_v4") if self.has("ips_v4") else []

    def set_ipv4_addresses(self, ips: set[str]) -> None:
        """
        Set the list of CloudFlare IPv4 addresses in the cache.

        Args:
            ips (set[str]): A set of IPv4 addresses to set in the cache.

        Returns:
            None: This function does not return anything.
        """
        self.set("ips_v4", ips)

    def get_ipv6_addresses(self) -> set[str]:
        """
        Get the list of CloudFlare IPv6 addresses from the cache.

        Returns:
            set[str]: A set of IPv6 addresses if the "ips_v6" key exists in the cache,
                      otherwise an empty set.
        """
        return self.get("ips_v6") if self.has("ips_v6") else []

    def set_ipv6_addresses(self, ips: set[str]) -> None:
        """
        Set the list of CloudFlare IPv6 addresses in the cache.

        Args:
            ips (set[str]): A set of IPv6 addresses to set in the cache.

        Returns:
            None: This function does not return anything.
        """
        self.set("ips_v6", ips)
