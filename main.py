import socket
import ipaddress
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from getmac import get_mac_address  # Make sure to install this library

def ping_host(ip):
    """Check if a host is alive by attempting to open a socket."""
    common_ports = [22, 80, 443]  # SSH, HTTP, HTTPS
    for port in common_ports:
        try:
            sock = socket.create_connection((ip, port), timeout=1)
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue
    return False

def scan_ports(ip, timeout=150):
    """Scan all ports (1-65535) on a given IP with a timeout."""
    open_ports = []
    start_time = time.time()

    for port in range(1, 65536):
        if time.time() - start_time > timeout:
            print(f"Port scanning timed out after {timeout} seconds.")
            break

        try:
            sock = socket.create_connection((ip, port), timeout=1)
            open_ports.append(port)
            sock.close()
        except (socket.timeout, ConnectionRefusedError):
            continue
    return open_ports

def get_os_version():
    """Get the operating system version."""
    return platform.platform()

def get_mac(ip):
    """Get the MAC address of the given IP."""
    mac = get_mac_address(ip=ip)
    return mac if mac else "MAC address not found"

def main():
    # Get user input for IP range
    ip_range = input("Enter the IP range to scan (e.g., 192.168.1.0/24): ")

    # Parse the IP range
    network = ipaddress.ip_network(ip_range)

    # Check for live hosts
    print(f"Scanning network: {ip_range}")
    live_hosts = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(ping_host, [str(ip) for ip in network.hosts()])
        for ip, is_alive in zip(network.hosts(), results):
            if is_alive:
                print(f"Live host found: {ip}")
                live_hosts.append(str(ip))

    # Scan all ports on live hosts and get OS and MAC address
    for host in live_hosts:
        print(f"\nScanning all ports on {host}...")
        open_ports = scan_ports(host)
        os_version = get_os_version()
        mac_address = get_mac(host)

        print(f"Open ports on {host}: {open_ports if open_ports else 'No open ports found.'}")
        print(f"Operating System: {os_version}")
        print(f"MAC Address: {mac_address}")

if __name__ == "__main__":
    main()
