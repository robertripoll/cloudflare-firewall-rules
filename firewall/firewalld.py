from enum import Enum
from subprocess import run, CalledProcessError

from firewall.base import Firewall, IPVersion


class Operation(Enum):
    """
    Enum representing the operation to perform on a firewall rule.

    Currently supported operations are SAVE (add) and DELETE (remove).
    """

    SAVE = 'add'
    DELETE = 'remove'


class Firewalld(Firewall):
    """
    Class representing a firewall using firewalld.

    This class provides methods to manage firewall rules.
    """

    def __init__(
        self,
        allowed_ports: set[int],
        ip_versions: set[IPVersion],
        is_permanent: bool = True,
        zone: str = "public",
    ):
        super().__init__(allowed_ports=allowed_ports, ip_versions=ip_versions)

        self.is_permanent = is_permanent
        self.zone = zone

    @staticmethod
    def __run_cmd(args: str | list[str]) -> None:
        if isinstance(args, str):
            args = [args]

        result = run(['firewall-cmd'] + args, user='root',
                     check=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise CalledProcessError(
                result.returncode, result.args, output=result.stdout, stderr=result.stderr)

    def __run_rule_cmd(self, operation: Operation, rule: str) -> None:
        args = []

        if self.is_permanent:
            args.append("--permanent")

        args.append("--zone=" + self.zone)
        args.append(f"--{operation.value}-rich-rule={rule}")

        Firewalld.__run_cmd(args)

    @staticmethod
    def __generate_rule(ip_address: str, ip_version: IPVersion, port: int) -> str:
        family = "ipv6" if ip_version == IPVersion.V6 else "ipv4"

        return (
            f'rule family="{family}" '
            f'source address="{ip_address.strip()}" '
            f'port port="{port}" '
            f'protocol="tcp" '
            "accept"
        )

    def __generate_rules_for_version(self, ip_address: str, ip_version: IPVersion) -> list[str]:
        rules: list[str] = []

        for port in self.allowed_ports:
            rules.append(self.__generate_rule(ip_address, ip_version, port))

        return rules

    def __generate_rules(self, ip_address: str) -> list[str]:
        rules_ipv4 = self.__generate_rules_for_version(
            ip_address, IPVersion.V4)
        rules_ipv6 = self.__generate_rules_for_version(
            ip_address, IPVersion.V6)

        return rules_ipv4 + rules_ipv6

    def is_rule_existing(self, ip_address: str) -> bool:
        rules = self.__generate_rules(ip_address)

        for rule in rules:
            self.__run_cmd(["--query-rich-rule", rule])

        return True

    def save_allow_rule(self, ip_address: str) -> bool:
        rules = self.__generate_rules(ip_address)

        for rule in rules:
            self.__run_rule_cmd(Operation.SAVE, rule)

        return True

    def delete_allow_rule(self, ip_address: str) -> bool:
        rules = self.__generate_rules(ip_address)

        for rule in rules:
            self.__run_rule_cmd(Operation.DELETE, rule)

        return True

    def sync(self) -> bool:
        self.__run_cmd("--reload")
        return True
