import argparse
import socket
import sys
import time

def main():
    print(f"[MOCK] Service starting with args: {sys.argv[1:]}")
    
    # Simple argument parsing to find --bind-addr
    bind_addr = "127.0.0.1:8080"
    if "--bind-addr" in sys.argv:
        try:
            idx = sys.argv.index("--bind-addr")
            bind_addr = sys.argv[idx + 1]
        except IndexError:
            pass
            
    host, port_str = bind_addr.split(":")
    port = int(port_str)
    
    print(f"[MOCK] Binding to {host}:{port}")
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print(f"[MOCK] Listening on {host}:{port}...")
        
        while True:
            client, addr = server.accept()
            try:
                # Read a bit of the request (optional, but good practice)
                client.settimeout(1.0)
                _ = client.recv(1024)
                
                # Send a simple HTTP response
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: text/html; charset=utf-8\r\n"
                    b"Connection: close\r\n"
                    b"\r\n"
                    b"<html><body>"
                    b"<h1>&#x1F680; Mock Code Server is Running!</h1>"
                    b"<p>If you see this, the Agent successfully started the service and FRP tunnel.</p>"
                    b"</body></html>"
                )
                client.sendall(response)
            except Exception as e:
                print(f"[MOCK] Error handling request: {e}")
            finally:
                client.close()
            
    except Exception as e:
        print(f"[MOCK] Failed to bind or listen: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
