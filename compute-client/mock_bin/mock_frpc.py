import sys
import socket
import threading
import time
import configparser
import os

def forward(source, destination):
    string = ' '
    while string:
        try:
            string = source.recv(1024)
            if string:
                destination.sendall(string)
            else:
                source.shutdown(socket.SHUT_RD)
                destination.shutdown(socket.SHUT_WR)
        except Exception:
            break

def handle_client(client_socket, target_host, target_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host, target_port))
        
        t1 = threading.Thread(target=forward, args=(client_socket, server_socket))
        t2 = threading.Thread(target=forward, args=(server_socket, client_socket))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
    except Exception as e:
        print(f"[MOCK FRPC] Connection error: {e}")
    finally:
        client_socket.close()

def main():
    print(f"[MOCK FRPC] Starting with args: {sys.argv}")
    sys.stdout.flush()
    
    # Parse arguments to find config file
    config_file = None
    if "-c" in sys.argv:
        try:
            idx = sys.argv.index("-c")
            config_file = sys.argv[idx + 1]
        except IndexError:
            pass
            
    if not config_file:
        print("[MOCK FRPC] No config file specified")
        sys.stdout.flush()
        while True: time.sleep(10)
        
    print(f"[MOCK FRPC] Reading config from {config_file}")
    sys.stdout.flush()
    
    if not os.path.exists(config_file):
        print(f"[MOCK FRPC] Config file not found: {config_file}")
        sys.stdout.flush()
        while True: time.sleep(10)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        print(f"[MOCK FRPC] Sections found: {config.sections()}")
        sys.stdout.flush()

        tunnel_setup = False
        
        # Find the first section that looks like a proxy
        for section in config.sections():
            if section == "common": continue
            
            print(f"[MOCK FRPC] Checking section: {section}")
            sys.stdout.flush()

            if "remote_port" in config[section] and "local_port" in config[section]:
                remote_port = int(config[section]["remote_port"])
                local_port = int(config[section]["local_port"])
                local_ip = config[section].get("local_ip", "127.0.0.1")
                
                print(f"[MOCK FRPC] Setting up tunnel: :{remote_port} -> {local_ip}:{local_port}")
                sys.stdout.flush()
                
                tunnel_setup = True
                
                try:
                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server.bind(("0.0.0.0", remote_port))
                    server.listen(5)
                    print(f"[MOCK FRPC] Listening on 0.0.0.0:{remote_port}")
                    sys.stdout.flush()
                    
                    while True:
                        client, addr = server.accept()
                        print(f"[MOCK FRPC] Accepted connection from {addr}")
                        sys.stdout.flush()
                        threading.Thread(target=handle_client, args=(client, local_ip, local_port)).start()
                        
                except Exception as e:
                    print(f"[MOCK FRPC] Failed to bind remote port {remote_port}: {e}")
                    sys.stdout.flush()
                    # Don't exit, just hang so process stays alive
                    while True: time.sleep(10)
        
        if not tunnel_setup:
            print("[MOCK FRPC] No valid tunnel configuration found in config file.")
            sys.stdout.flush()
            while True: time.sleep(10)
                    
    except Exception as e:
        print(f"[MOCK FRPC] Error parsing config: {e}")
        sys.stdout.flush()
        while True: time.sleep(10)

if __name__ == "__main__":
    main()
