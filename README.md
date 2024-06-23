# Cloudflare Firewall Rules

This project is a tool for synchronizing firewall rules with the latest Cloudflare IP addresses.
It adds rules to `firewalld` allowing traffic coming from Cloudflare IP addresses on port 443.

## Requirements

This project requires Python 3.6 or higher.

## Installation

To install the project, follow these steps:

1. Clone the repository:

`git clone https://github.com/your-username/cloudflare-ip-sync.git`

2. Install the dependencies:

`pip install -r requirements.txt`

## Usage

To use the project, run the following command:

`python main.py`

This will synchronize the firewall rules with the latest Cloudflare IP addresses.

## Configuration

The project requires the following configuration:

- `CLOUDFLARE_IPS_CACHE_PATH`: The path to the cache file for Cloudflare IP addresses.
- `FIREWALL_HTTPS_PORT`: The HTTPS port to allow in the firewall.

These configuration values can be set in the `config.py` file.

## License

This project is licensed under the [MIT License](LICENSE).
