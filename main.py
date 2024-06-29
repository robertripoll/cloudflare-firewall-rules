"""
This module contains the main entry point of the application.

It manages the synchronization of firewall rules with the latest Cloudflare IP addresses.

It retrieves the latest IPv4 and IPv6 addresses from the Cloudflare API and compares them with the
cached IP addresses.

If the cached ETag is different from the latest ETag, it removes the old allow rules and adds the
new allow rules.

The firewall rules are saved to the `firewalld` and synchronized.

The latest ETag is cached for future comparisons.
"""

from cache.base import Cache
from cache.file_cache import FileCache
from cloudflare.base import CloudFlare
from firewall.base import Firewall, IPVersion, SyncableFirewall
from firewall.firewalld import Firewalld


def remove_old_allow_rules(ipv4: set[str], ipv6: set[str], firewall: Firewall) -> bool:
    """
    Removes old allow rules for IPv4 and IPv6 from the given firewall.

    Args:
        ipv4 (set[str]): A set of IPv4 addresses for which old allow rules should be removed.
        ipv6 (set[str]): A set of IPv6 addresses for which old allow rules should be removed.
        firewall (Firewall): An instance of the Firewall class representing the firewall.

    Returns:
        bool: True if all old allow rules were successfully removed, False otherwise.
    """
    if not firewall.delete_allow_rules(ipv4, IPVersion.V4):
        return False

    if not firewall.delete_allow_rules(ipv6, IPVersion.V6):
        return False

    return True


def add_new_allow_rules(ipv4: set[str], ipv6: set[str], firewall: Firewall) -> bool:
    """
    Adds new allow rules to the firewall.

    Args:
        ipv4 (set[str]): A set of IPv4 addresses for which to add allow rules.
        ipv6 (set[str]): A set of IPv6 addresses for which to add allow rules.
        firewall (Firewall): An instance of the Firewall class representing the firewall.

    Returns:
        bool: True if all allow rules were successfully added, False otherwise.
    """
    if not firewall.save_allow_rules(ipv4, IPVersion.V4):
        return False

    if not firewall.save_allow_rules(ipv6, IPVersion.V6):
        return False

    if issubclass(type(firewall), SyncableFirewall):
        syncable_firewall: SyncableFirewall = firewall
        return syncable_firewall.sync()

    return True


def main():
    """
    The main function of the program.

    This function performs the following steps:
    1. Initializes a cache using the FileCache class.
    2. Initializes a CloudFlare object.
    3. Retrieves the cached ETag from the cache.
    4. Retrieves the latest IPv4 and IPv6 addresses from the CloudFlare API.
    5. If the cached ETag is the same as the latest ETag, the function returns.
    6. Initializes a firewall object using the Firewalld class.
    7. If there is a cached ETag, retrieves the cached IPv4 and IPv6 addresses from the cache.
    8. Removes the old allow rules from the firewall using the cached IPv4 and IPv6 addresses.
    9. Adds new allow rules to the firewall using the latest IPv4 and IPv6 addresses.
    10. Synchronizes the firewall rules.
    11. Sets the latest ETag in the cache.

    Returns:
        None

    Example:
        >>> main()
    """

    cache: Cache = FileCache()
    cloudflare = CloudFlare()

    cached_etag = cache.get("etag")
    last_ips_v4, last_ips_v6, last_etag = cloudflare.get_ips()

    if cached_etag == last_etag:
        return

    firewall: Firewall = Firewalld({443})

    if cached_etag is not None:
        cached_ipv4: set[str] = cache.get('ipv4')
        cached_ipv6: set[str] = cache.get('ipv6')

        remove_old_allow_rules(cached_ipv4, cached_ipv6, firewall)

    add_new_allow_rules(last_ips_v4, last_ips_v6, firewall)

    firewall.sync()
    cache.set("etag", last_etag)


if __name__ == '__main__':
    main()
