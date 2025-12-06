import enum
import socket
import netifaces


class DeploymentType(enum.Enum):
    LOCALHOST = 1
    WIFI = 2
    VPN = 3


DEPLOYMENT_TYPE = DeploymentType.WIFI


def GET_IP() -> str:
    """Returns the IP address according to DEPLOYMENT_TYPE"""
    if DEPLOYMENT_TYPE == DeploymentType.LOCALHOST:
        return "127.0.0.1"

    elif DEPLOYMENT_TYPE == DeploymentType.WIFI:
        # Recupera l'IP privato della macchina
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Non serve connettersi realmente, basta l'indirizzo della destinazione
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    elif DEPLOYMENT_TYPE == DeploymentType.VPN:
        # Tenta di recuperare un IP VPN: spesso è l'interfaccia predefinita diversa da WIFI
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip.startswith("127."):
                # fallback, potrebbe esserci un'interfaccia VPN diversa
                for iface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip_candidate = addr.get("addr")
                            if ip_candidate and not ip_candidate.startswith("127."):
                                return ip_candidate
                return "127.0.0.1"
            return ip
        except Exception:
            return "127.0.0.1"
