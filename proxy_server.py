import socket
import select
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# External proxy configuration
PROXY_HOST = "superproxy.zenrows.com"
PROXY_PORT = 1337
PROXY_AUTH = "QyzrrxUUDxwb:otr4mBs_country-ar_ttl-24h_session-VKQ7LuInGHe5"

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        """Handles CONNECT requests to establish HTTPS tunnels."""
        try:
            # Parse the destination host and port
            host, port = self.path.split(":")
            port = int(port)

            # Encode credentials for Proxy-Authorization
            auth_header = base64.b64encode(PROXY_AUTH.encode()).decode()

            # Connect to the external proxy with a timeout
            with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=10) as proxy_socket:
                proxy_socket.settimeout(10)  # Maximum wait time for operations

                # Send CONNECT request to the external proxy
                connect_request = (
                    f"CONNECT {host}:{port} HTTP/1.1\r\n"
                    f"Host: {host}:{port}\r\n"
                    f"Proxy-Authorization: Basic {auth_header}\r\n"
                    "\r\n"
                )
                proxy_socket.sendall(connect_request.encode("utf-8"))

                # Read the response from the external proxy
                proxy_response = proxy_socket.recv(4096)
                if b"200 Connection established" not in proxy_response:
                    self.send_error(502, "Bad Gateway: Proxy did not establish tunnel")
                    return

                # Respond to the client to establish the tunnel
                self.send_response(200, "Connection established")
                self.end_headers()

                # Redirect traffic between client and proxy
                self._forward_traffic(self.connection, proxy_socket)
        except Exception as e:
            self.send_error(500, f"Error handling CONNECT: {str(e)}")

    def do_GET(self):
        """Handles GET requests through the external proxy."""
        self._handle_http_request()

    def do_POST(self):
        """Handles POST requests through the external proxy."""
        self._handle_http_request()

    def _handle_http_request(self):
        """Processes standard HTTP requests and forwards them to the external proxy."""
        try:
            # Build the HTTP request to send to the external proxy
            auth_header = base64.b64encode(PROXY_AUTH.encode()).decode()
            request_headers = f"{self.command} {self.path} HTTP/1.1\r\n"

            # Forward all client headers
            for header, value in self.headers.items():
                request_headers += f"{header}: {value}\r\n"
            
            # Add proxy authentication
            request_headers += f"Proxy-Authorization: Basic {auth_header}\r\n"
            request_headers += "\r\n"

            # Read the body of the request (if applicable, e.g. POST)
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""

            # Connect to the external proxy
            with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=10) as proxy_socket:
                # Send the request to the external proxy
                proxy_socket.sendall(request_headers.encode("utf-8") + body)

                # Receive the response from the external proxy
                self._forward_response(proxy_socket)
        except Exception as e:
            self.send_error(500, f"Error handling HTTP request: {str(e)}")

    def _forward_response(self, proxy_socket):
        """Forwards the external proxy's response to the client."""
        try:
            while True:
                data = proxy_socket.recv(4096)
                if not data:  # Close if no more data
                    break
                self.connection.sendall(data)
        except Exception as e:
            print(f"Error during response forwarding: {str(e)}")

    def _forward_traffic(self, client_socket, proxy_socket):
        """Forwards traffic between the client and the proxy (used for CONNECT)."""
        sockets = [client_socket, proxy_socket]
        try:
            while True:
                # Wait for data from any socket
                readable, _, _ = select.select(sockets, [], [])
                for sock in readable:
                    data = sock.recv(4096)
                    if not data:  # Close if no data
                        return
                    # Forward data
                    if sock is client_socket:
                        proxy_socket.sendall(data)
                    else:
                        client_socket.sendall(data)
        except Exception as e:
            print(f"Error during data forwarding: {str(e)}")
        finally:
            # Always close both sockets
            client_socket.close()
            proxy_socket.close()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Multithreaded server to handle multiple simultaneous connections."""
    daemon_threads = True

def run(server_class=ThreadingHTTPServer, handler_class=ProxyHTTPRequestHandler, port=8080):
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting proxy server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
