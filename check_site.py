import os
from dotenv import load_dotenv
import click
import requests
import socket
import dns.resolver

# Load environment variables from .env file
load_dotenv()

@click.command()
@click.argument('url', required=False)
@click.option('--version', '-v', is_flag=True, help='Display the version of the tool')
def check_site(url, version):
    """
    Check the status and DNS information of a website.

    Args:
        url (str): The URL of the website to check.
        version (bool): Flag to display the version of the tool.
    """
    if version:
        display_version()
        return

    if not url:
        click.echo("Error: Missing argument 'URL'.")
        return

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    try:
        response = requests.get(url, allow_redirects=False)
        status_code = response.status_code

        if 200 <= status_code < 300:
            click.echo("--\nSite Status - Online")
            click.echo("Status Code - {}".format(status_code))
            dns_info = get_dns_info(url)
            click.echo("--\nDNS Information\n--")
            click.echo(dns_info)
        elif 300 <= status_code < 400:
            redirect_url = response.headers['Location']
            redirect_response = requests.get(redirect_url)
            if 200 <= redirect_response.status_code < 300:
                click.echo("--\nSite Status - Online")
                click.echo("Status Code - {}".format(redirect_response.status_code))
                dns_info = get_dns_info(redirect_url)
                click.echo("--\nDNS Information\n--")
                click.echo(dns_info)
            else:
                click.echo("--\nSite Status - Offline")
        else:
            click.echo("--\nSite Status - Offline")
    except Exception as e:
        click.echo("An error occurred:", e)

def display_version():
    """Display the version of the tool."""
    version = os.getenv('version', 'v0.0.0')
    os_platform = os.uname().sysname
    version = version.lstrip('v')  # Remove leading 'v'
    click.echo(f"Version: {version}\nOS Platform: {os_platform}")

def get_dns_info(url):
    """
    Get DNS information for a given URL.

    Args:
        url (str): The URL of the website.

    Returns:
        str: DNS information for the website.
    """
    dns_info = ""
    domain = url.split('//')[-1].split('/')[0]
    try:
        ip_address = socket.gethostbyname(domain)
        dns_info += "IP: {}\n".format(ip_address)
    except Exception as e:
        pass

    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        for rdata in answers:
            dns_info += "CNAME: {}\n".format(rdata.target.to_text().strip('.'))
            break
    except Exception as e:
        pass

    return dns_info.strip()

if __name__ == '__main__':
    check_site()
