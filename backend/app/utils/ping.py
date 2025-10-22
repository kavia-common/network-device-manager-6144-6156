"""Cross-platform ping utility using subprocess."""

import platform
import subprocess

# PUBLIC_INTERFACE
def ping_host(host: str, timeout_seconds: int = 2) -> bool:
    """Ping a host once and return True if reachable.

    Args:
        host: Hostname or IP address to ping.
        timeout_seconds: Command timeout.

    Returns:
        bool: True if ping succeeded, False otherwise.
    """
    system = platform.system().lower()
    if "windows" in system:
        # -n 1 -> one echo request, -w timeout in ms
        cmd = ["ping", "-n", "1", "-w", str(int(timeout_seconds * 1000)), host]
    else:
        # -c 1 -> one packet, -W timeout in seconds (Linux)
        # macOS uses -W in ms for ping6 and doesn't support for ping; use -t for TTL; use timeout via subprocess
        cmd = ["ping", "-c", "1", "-W", str(timeout_seconds), host]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_seconds + 1,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False
