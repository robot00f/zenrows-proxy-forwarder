---
# Proxy Server with External Proxy Support

## Overview

This Python-based proxy server allows for HTTP and HTTPS traffic forwarding through an external proxy server. It supports `CONNECT` requests for establishing secure HTTPS tunnels and forwards `GET` and `POST` requests via an external proxy with authentication. The server is multithreaded to handle multiple simultaneous client connections.

## Features

- **HTTPS Tunneling:** Handles `CONNECT` requests to establish HTTPS tunnels, enabling secure communication between clients and destination servers.
- **External Proxy Support:** Forwards both HTTP and HTTPS requests to an external proxy server.
- **Proxy Authentication:** Supports Basic Authentication for connecting to an external proxy.
- **Multithreaded:** Uses a `ThreadingHTTPServer` to handle multiple concurrent connections.
- **Error Handling:** Includes error handling for connection issues and request forwarding problems.
  
## Requirements

- Python 3.x
- `base64`, `socket`, `select`, and `http.server` modules (standard Python libraries)
- External Proxy Server (configure `PROXY_HOST`, `PROXY_PORT`, and `PROXY_AUTH`)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/robot00f/zenrows-proxy-forwarder.git
   cd zenrows-proxy-forwarder
   ```

2. **Set up the external proxy:**

   - Open the `proxy_server.py` file.
   - Set the following variables to match your external proxy's configuration:
     - `PROXY_HOST`: The hostname or IP address of the external proxy.
     - `PROXY_PORT`: The port of the external proxy (default: 1337).
     - `PROXY_AUTH`: Your proxy authentication credentials in the format `username:password`.

   Example:
   ```python
   PROXY_HOST = "superproxy.zenrows.com"
   PROXY_PORT = 1337
   PROXY_AUTH = "Qbzr2xXXDxwb:otr0m4s_country-ar_ttl-24h_session-VAQ7LuInGoe5"
   ```

3. **Run the proxy server:**

   ```bash
   python proxy_server.py
   ```

   By default, the server will listen on port `8080`. You can change the port by modifying the `run()` function in the `proxy_server.py` file.

4. **Access the Proxy Server:**

   The proxy server will listen on all available interfaces (`0.0.0.0`) and can be accessed via port 8080 (or a custom port if configured). Configure your client (browser, application, etc.) to use the proxy server with the IP address of the machine and the specified port.

## How It Works

### HTTP/HTTPS Request Handling

The proxy server handles both standard HTTP requests (`GET`, `POST`) and HTTPS requests (`CONNECT`). When a client makes a request:

1. **`CONNECT` Request (HTTPS):**
   - The server receives a `CONNECT` request from the client, which is used to establish an HTTPS tunnel.
   - It parses the target host and port and then connects to the external proxy server.
   - The server sends a `CONNECT` request to the external proxy with the provided authentication credentials.
   - If the external proxy successfully establishes the connection, the server responds to the client, confirming the tunnel establishment.
   - The server then forwards the traffic between the client and the external proxy.

2. **HTTP `GET`/`POST` Requests:**
   - For standard HTTP requests, the proxy forwards the request to the external proxy, adding necessary headers such as `Proxy-Authorization`.
   - It also forwards any body content for `POST` requests.
   - Once the response is received from the external proxy, the server forwards the response back to the client.

### Traffic Forwarding

- For both `CONNECT` and HTTP requests, the server uses non-blocking sockets and the `select.select()` method to forward data between the client and the external proxy.
- Data is forwarded as it arrives in chunks, with the server handling multiple connections simultaneously using multithreading.

### Error Handling

- If there’s a failure in establishing a connection with the external proxy or an issue with forwarding the data, the server returns appropriate error codes to the client:
  - `502 Bad Gateway` if the proxy cannot establish the tunnel.
  - `500 Internal Server Error` for other errors, such as connection timeouts or request handling failures.

## Configuration

### Proxy Host & Port

Edit the `PROXY_HOST` and `PROXY_PORT` variables to match your external proxy's host and port.

### Proxy Authentication

- The `PROXY_AUTH` variable should be set to the credentials required for Basic Authentication in the format `username:password`.
- The server will automatically encode these credentials in the `Proxy-Authorization` header.

### Server Port

- The server listens on port 8080 by default. To change this, modify the `port` argument in the `run()` function.

Example:
```python
run(server_class=ThreadingHTTPServer, handler_class=ProxyHTTPRequestHandler, port=8081)
```

## Example Usage

1. Start the server by running:

   ```bash
   python proxy_server.py
   ```

2. Set your web browser or application to use `http://<your-server-ip>:8080` as the proxy.

3. Make an HTTP or HTTPS request through the configured proxy. The server will forward the request to the external proxy, receive the response, and send it back to the client.

## Troubleshooting

- **Connection Issues:**
  - Ensure that the external proxy is up and reachable from the machine running the proxy server.
  - Verify that the proxy credentials are correct.
  
- **Server Timeout:**
  - The proxy server has a 10-second timeout for both connection and data operations. If the external proxy is slow to respond, you may need to adjust the timeout or troubleshoot the external proxy.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
