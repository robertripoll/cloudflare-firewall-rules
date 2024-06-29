"""
This module defines the abstract base class for firewalls.

This module provides the `Firewall` abstract base class that defines the interface
for firewalls. It also defines the `IPVersion` enum that represents the version of an IP address.
"""

from abc import ABC, abstractmethod
from enum import Enum


class IPVersion(Enum):
    """
    Enum representing the version of an IP address.

    Currently supported versions are V4 (IPv4) and V6 (IPv6).
    """

    V4 = 4
    V6 = 6


class Firewall(ABC):
    """
    Abstract base class for firewalls.

    This class defines the interface for firewalls.
    """

    def __init__(
        self,
        allowed_ports: set[int],
        ip_versions: set[IPVersion] = None,
    ):
        """
        Initializes the Firewall object with the given allowed ports and IP versions.

        Args:
            allowed_ports (set[int]): A set of allowed ports for the firewall.
            ip_versions (set[IPVersion]): A set of IP versions for the firewall.

        Returns:
            None
        """
        self.allowed_ports = allowed_ports
        self.ip_versions = ip_versions if ip_versions is not None else {
            IPVersion.V4, IPVersion.V6}

    @abstractmethod
    def is_rule_existing(self, ip_address: str, ip_version: IPVersion) -> bool:
        """
        Check if a rule already exists for the given IP address and IP version.

        Args:
            ip_address (str): The IP address to check for an existing rule.
            ip_version (IPVersion): The IP version for the rule.

        Returns:
            bool: True if a rule exists for the given IP address and IP version, False otherwise.
        """

    @abstractmethod
    def save_allow_rule(self, ip_address: str, ip_version: IPVersion) -> bool:
        """
        Save an allow rule for the given IP address.

        Args:
            ip_address (str): The IP address for which to save the allow rule.
            ip_version (IPVersion): The IP version for the allow rule.

        Returns:
            bool: True if the allow rule was successfully saved, False otherwise.
        """

    def save_allow_rules(self, ip_address: set[str], ip_version: IPVersion) -> bool:
        """
        Save allow rules for multiple IP addresses.

        Args:
            ip_address (set[str]): A set of IP addresses for which to save the allow rules.
            ip_version (IPVersion): The IP version for the allow rules.

        Returns:
            bool: True if all allow rules were successfully saved, False otherwise.
        """
        for ip in ip_address:
            if not self.save_allow_rule(ip, ip_version):
                return False

        return True

    @abstractmethod
    def delete_allow_rule(self, ip_address: str, ip_version: IPVersion) -> bool:
        """
        Delete an allow rule for the given IP address and IP version.

        Args:
            ip_address (str): The IP address for which to delete the allow rule.
            ip_version (IPVersion): The IP version for the allow rule.

        Returns:
            bool: True if the allow rule was successfully deleted, False otherwise.
        """

    def delete_allow_rules(self, ip_address: set[str], ip_version: IPVersion) -> bool:
        """
        Delete allow rules for multiple IP addresses.

        Args:
            ip_address (set[str]): A set of IP addresses for which to delete the allow rules.
            ip_version (IPVersion): The IP version for the allow rules.

        Returns:
            bool: True if all allow rules were successfully deleted, False otherwise.
        """
        for ip in ip_address:
            if not self.delete_allow_rule(ip, ip_version):
                return False

        return True


class SyncableFirewall(Firewall):
    """
    Interface for firewalls that can be synchronized.

    This interface defines the methods that subclasses must implement to provide a
    synchronization mechanism for updating firewall rules based on the current state of
    the firewall.
    """

    @abstractmethod
    def sync(self) -> bool:
        """
        Abstract method that should be implemented by subclasses to synchronize the firewall rules.

        This method should perform the necessary actions to update the firewall rules based on the
        current state of the firewall.

        Returns:
            bool: True if the synchronization was successful, False otherwise.
        """
