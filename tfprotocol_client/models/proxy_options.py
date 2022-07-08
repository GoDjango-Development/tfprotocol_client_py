# coded by lagcleaner
# email: lagcleaner@gmail.com

class ProxyOptions:
    """Proxy Options model to contain the options in case of proxy usage.
    """

    def __init__(
        self, proxy_type, address: str, port: int, username: str, password: str,
    ) -> None:
        """Proxy Options container

        Args:
            `proxy_type` (proxy type): The type of the proxy to be used. Three types are
                supported: PROXY_TYPE_SOCKS4 (including socks4a), PROXY_TYPE_SOCKS5 and
                PROXY_TYPE_HTTP.
            `address` (str): The address of the server (IP or DNS).
            `port` (int): The port of the server. Defaults to 1080 for SOCKS servers and 8080 for
                HTTP proxy servers.
            `username` (str): Username to authenticate with to the server. The default is no
                authentication. (Optional)
            `password` (str): Password to authenticate with to the server. Only relevant when
                username is also provided. (Optional)
        """
        self.proxy_type = proxy_type
        self.port = port
        self.address = address
        self.username = username
        self.password = password
