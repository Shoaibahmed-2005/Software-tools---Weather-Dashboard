"""
network_check.py — Experiment 5: Python Network Interface Checker
Checks all active network interfaces and tests connectivity to the Flask server.
Run independently:  python server/network_check.py
"""
import socket
import subprocess
import platform
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000


def get_interfaces():
    """List all network interfaces and their IP addresses."""
    print("=" * 55)
    print("  NETWORK INTERFACE CHECKER — Weather Station")
    print("=" * 55)

    hostname = socket.gethostname()
    print(f"\n Hostname     : {hostname}")

    try:
        # Primary IP
        primary_ip = socket.gethostbyname(hostname)
        print(f" Primary IP   : {primary_ip}")
    except Exception:
        print(" Primary IP   : Unable to resolve")

    # Attempt to list interfaces via socket
    print("\n Active Network Interfaces:")
    print("-" * 40)

    try:
        import psutil
        ifaces = psutil.net_if_addrs()
        stats  = psutil.net_if_stats()
        for iface, addrs in ifaces.items():
            is_up = stats[iface].isup if iface in stats else False
            status = "UP  " if is_up else "DOWN"
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"  [{status}] {iface:<20} {addr.address}")
    except ImportError:
        # Fallback without psutil
        try:
            result = subprocess.run(
                ['ipconfig'] if platform.system() == 'Windows' else ['ip', 'addr'],
                capture_output=True, text=True, timeout=5
            )
            print(result.stdout[:1500])
        except Exception as e:
            print(f"  Could not list interfaces: {e}")


def check_server_reachability(host=SERVER_HOST, port=SERVER_PORT, timeout=3):
    """Test if the Flask weather server is reachable on the given port."""
    print(f"\n Server Reachability Check")
    print("-" * 40)
    print(f"  Target : {host}:{port}")
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print(f"  Status : ✓ REACHABLE — Server is running!")
        return True
    except socket.timeout:
        print(f"  Status : ✗ TIMEOUT — Server not responding in {timeout}s")
    except ConnectionRefusedError:
        print(f"  Status : ✗ REFUSED — Server is not running on port {port}")
    except Exception as e:
        print(f"  Status : ✗ ERROR — {e}")
    return False


def check_internet(host='8.8.8.8', port=53, timeout=3):
    """Check external internet connectivity (Google DNS)."""
    print(f"\n Internet Connectivity Check")
    print("-" * 40)
    print(f"  Target : Google DNS ({host}:{port})")
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        print("  Status : ✓ Internet is REACHABLE")
        return True
    except Exception:
        print("  Status : ✗ No internet connection")
    return False


def dns_lookup(domain='localhost'):
    """Resolve a hostname to IP."""
    print(f"\n DNS Lookup: {domain}")
    print("-" * 40)
    try:
        ip = socket.gethostbyname(domain)
        print(f"  {domain} → {ip}")
    except Exception as e:
        print(f"  Failed: {e}")


if __name__ == '__main__':
    get_interfaces()
    check_internet()
    check_server_reachability()
    dns_lookup('localhost')
    print("\n" + "=" * 55)
    print("  Network check complete.")
    print("=" * 55 + "\n")
