from cache.base import Cache
from cache.file_cache import FileCache
from cloudflare.base import CloudFlare
from firewall.base import Firewall
from firewall.firewalld import Firewalld


def main():
    cache: Cache = FileCache()
    cloudflare = CloudFlare()

    cached_etag = cache.get("etag")
    last_ips_v4, last_ips_v6, last_etag = cloudflare.get_ips()

    if cached_etag == last_etag:
        return

    firewall: Firewall = Firewalld()

    if cached_etag != None:
        cached_ipv4 = cache.get('ipv4')
        cached_ipv6 = cache.get('ipv6')

        # delete existing firewall rules

        pass

    for ip in last_ips_v4:
        firewall.save_allow_rule(ip)

    for ip in last_ips_v6:
        firewall.save_allow_rule(ip)

    firewall.sync()
    cache.set("etag", last_etag)


if __name__ == '__main__':
    main()
