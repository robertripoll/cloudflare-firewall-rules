from cache.base import Cache
from cache.file_cache import FileCache
from cloudflare.base import CloudFlare
from firewall.base import Firewall, IPVersion, SyncableFirewall
from firewall.firewalld import Firewalld


def remove_old_allow_rules(ipv4: set[str], ipv6: set[str], firewall: Firewall) -> bool:
    if not firewall.delete_allow_rules(ipv4, IPVersion.V4):
        return False

    if not firewall.delete_allow_rules(ipv6, IPVersion.V6):
        return False

    return True


def add_new_allow_rules(ipv4: set[str], ipv6: set[str], firewall: Firewall) -> bool:
    if not firewall.save_allow_rules(ipv4, IPVersion.V4):
        return False

    if not firewall.save_allow_rules(ipv6, IPVersion.V6):
        return False

    if issubclass(type(firewall), SyncableFirewall):
        return firewall.sync()

    return True


def main():
    cache: Cache = FileCache()
    cloudflare = CloudFlare()

    cached_etag = cache.get("etag")
    last_ips_v4, last_ips_v6, last_etag = cloudflare.get_ips()

    if cached_etag == last_etag:
        return

    firewall: Firewall = Firewalld()

    if cached_etag != None:
        cached_ipv4: set[str] = cache.get('ipv4')
        cached_ipv6: set[str] = cache.get('ipv6')

        remove_old_allow_rules(cached_ipv4, cached_ipv6, firewall)

    firewall.save_allow_rules(last_ips_v4, IPVersion.V4)
    firewall.save_allow_rules(last_ips_v6, IPVersion.V6)

    firewall.sync()
    cache.set("etag", last_etag)


if __name__ == '__main__':
    main()
