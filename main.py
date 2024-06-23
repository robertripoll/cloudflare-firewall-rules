from typing import List
import json
import requests
import os
import subprocess

CLOUDFLARE_IPS_ENDPOINT = "https://api.cloudflare.com/client/v4/ips"
CLOUDFLARE_IPS_CACHE_PATH = "/tmp/cloudflare_ips.json"

FIREWALL_HTTPS_PORT = 443


def get_last_cloudflare_ips() -> tuple[List[str], List[str], str]:
    """
    Retrieves the latest Cloudflare IP addresses.

    Returns:
        tuple[List[str], List[str], str]: A tuple containing two lists of IPv4 and IPv6 addresses, and a string representing the etag.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.request(
        "GET", CLOUDFLARE_IPS_ENDPOINT, headers=headers)

    if not response.ok or response.status_code != 200:
        raise Exception(f"Request failed with status code {
                        response.status_code}")

    data = response.json()  # type: dict

    if not data.get("success"):
        raise Exception(f"Request failed with errors {data.get('errors')}")

    result = data.get("result")  # type: dict

    etag = result.get("etag")  # type: str
    ips_v4 = result.get("ipv4_cidrs", [])  # type: List[str]
    ips_v6 = result.get("ipv6_cidrs", [])  # type: List[str]

    return ips_v4, ips_v6, etag


def get_cached_cloudflare_ips():
    """
    Retrieves the cached Cloudflare IP addresses from the cache file.

    Returns:
        tuple[List[str], List[str], str] or None: A tuple containing two lists of IPv4 and IPv6 addresses, and a string representing the etag.
        If the cache file does not exist, returns None.
    """
    if not os.path.isfile(CLOUDFLARE_IPS_CACHE_PATH):
        return None

    # read file
    with open(CLOUDFLARE_IPS_CACHE_PATH, 'r') as file:
        data = file.read()

    # parse json
    cache = json.loads(data)  # type: dict

    # get values
    etag = cache.get("etag")  # type: str
    ips = cache.get("ips")  # type: dict[str, List[str]]

    ips_v4 = ips.get("v4")  # type: List[str]
    ips_v6 = ips.get("v6")  # type: List[str]

    return ips_v4, ips_v6, etag


def set_cached_cloudflare_ips(ips_v4: List[str], ips_v6: List[str], etag: str):
    """
    Writes the given Cloudflare IP addresses, IPv4 and IPv6, and the ETag to the cache file.

    Args:
        ips_v4 (List[str]): A list of IPv4 addresses.
        ips_v6 (List[str]): A list of IPv6 addresses.
        etag (str): The ETag.

    Returns:
        None
    """
    # create cache
    cache = {
        "etag": etag,
        "ips": {
            "v4": ips_v4,
            "v6": ips_v6
        }
    }

    # write cache
    with open(CLOUDFLARE_IPS_CACHE_PATH, 'w') as file:
        file.write(json.dumps(cache))


def run_firewall_cmd(args: str | List[str]):
    """
    Runs a firewall command with the given arguments.

    Args:
        args (str | List[str]): The arguments to pass to the firewall command.

    Raises:
        Exception: If the firewall command fails to run.

    Returns:
        None
    """
    if type(args) == str:
        args = [args]

    print(f"Running firewall command: {' '.join(args)}")

    result = subprocess.run(
        ['firewall-cmd'] + args, user='root', check=True, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception("Could not run firewall command", result.stderr)


def generate_firewall_rule_args(operation: str, rule: str):
    """
    Generates the arguments for a firewall rule.

    Args:
        operation (str): The operation to perform on the firewall rule.
        rule (str): The rule to be added or removed.

    Returns:
        list: A list of arguments for the firewall command.
    """
    args = ["--permanent", "--zone=public", f"--{operation}-rich-rule={rule}"]
    return args


def run_firewall_set_rule_cmd(rule: str):
    """
    Run the firewall command to add a rule.

    Args:
        rule (str): The rule to be added.

    Returns:
        None
    """
    args = generate_firewall_rule_args("add", rule)
    run_firewall_cmd(args)


def run_firewall_unset_rule_cmd(rule: str):
    """
    Run the firewall command to remove a rule.

    Args:
        rule (str): The rule to be removed.

    Returns:
        None
    """
    args = generate_firewall_rule_args("remove", rule)
    run_firewall_cmd(args)


def generate_firewall_rule(ip: str, is_ipv6: bool):
    """
    Generates a firewall rule for the given IP address and IPv6 flag.

    Args:
        ip (str): The IP address to generate the firewall rule for.
        is_ipv6 (bool): A flag indicating whether the IP address is IPv6.

    Returns:
        str: The generated firewall rule as a string.
    """
    family = "ipv6" if is_ipv6 else "ipv4"

    return f'rule family="{family.strip()}" source address="{ip.strip()}" port port="{FIREWALL_HTTPS_PORT}" protocol="tcp" accept'


def set_firewall_rule(ip: str, is_ipv6: bool):
    """
    Set a firewall rule for the given IP address and IPv6 flag.

    Args:
        ip (str): The IP address to set the firewall rule for.
        is_ipv6 (bool): A flag indicating whether the IP address is IPv6.

    Returns:
        None
    """
    rule = generate_firewall_rule(ip, is_ipv6)
    run_firewall_set_rule_cmd(rule)


def set_firewall_rules(ips_v4: List[str], ips_v6: List[str]):
    """
    Sets firewall rules for the given lists of IPv4 and IPv6 addresses.

    Args:
        ips_v4 (List[str]): A list of IPv4 addresses.
        ips_v6 (List[str]): A list of IPv6 addresses.

    Returns:
        None
    """
    for ip in ips_v4:
        set_firewall_rule(ip, False)

    for ip in ips_v6:
        set_firewall_rule(ip, True)


def unset_firewall_rule(ip: str, is_ipv6: bool):
    """
    Unsets a firewall rule for the given IP address and IPv6 flag.

    Args:
        ip (str): The IP address to unset the firewall rule for.
        is_ipv6 (bool): A flag indicating whether the IP address is IPv6.

    Returns:
        None
    """
    rule = generate_firewall_rule(ip, is_ipv6)
    run_firewall_unset_rule_cmd(rule)


def unset_firewall_rules(ips_v4: List[str], ips_v6: List[str]):
    """
    Unsets firewall rules for the given lists of IPv4 and IPv6 addresses.

    Args:
        ips_v4 (List[str]): A list of IPv4 addresses.
        ips_v6 (List[str]): A list of IPv6 addresses.

    Returns:
        None
    """
    for ip in ips_v4:
        unset_firewall_rule(ip, False)

    for ip in ips_v6:
        unset_firewall_rule(ip, True)


def sync_firewall_rules():
    """
    Synchronizes the firewall rules by reloading the firewall configuration.

    This function does not take any parameters.

    Returns:
        None
    """
    run_firewall_cmd("--reload")


def sync_cloudflare_ips():
    """
    Synchronizes the Cloudflare IP addresses by comparing the cached IP addresses with the latest IP addresses.
    If the ETag of the cached IP addresses matches the ETag of the latest IP addresses, no synchronization is performed.
    Otherwise, the firewall rules are unset for the cached IP addresses, the firewall rules are set for the latest IP addresses,
    and the latest IP addresses are cached with their ETag.

    This function does not take any parameters.

    Returns:
        None
    """
    cached_data = get_cached_cloudflare_ips()

    if cached_data is None:
        cached_ips_v4 = []
        cached_ips_v6 = []
        cached_etag = None
    else:
        cached_ips_v4, cached_ips_v6, cached_etag = cached_data

    last_ips_v4, last_ips_v6, last_etag = get_last_cloudflare_ips()

    if cached_etag == last_etag:
        return

    if cached_data is not None:
        unset_firewall_rules(cached_ips_v4, cached_ips_v6)

    set_firewall_rules(last_ips_v4, last_ips_v6)
    set_cached_cloudflare_ips(last_ips_v4, last_ips_v6, last_etag)
    sync_firewall_rules()


def main():
    sync_cloudflare_ips()


if __name__ == '__main__':
    main()
