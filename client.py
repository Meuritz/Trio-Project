import socket

# Define the server address and port
SERVER_HOST = "localhost"
SERVER_PORT = 60420

def start_client():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server: {SERVER_HOST}:{SERVER_PORT}")
    
    # Receive the prompt for the username
    prompt = client_socket.recv(1024).decode('utf-8')
    print(prompt)
    
    # Send the username to the server
    username = input()
    client_socket.send(username.encode('utf-8'))
    
    return client_socket

def client_loop():
    
    client_socket = start_client()
    
    try:
        while True:
            # Receive response from server
            response = client_socket.recv(1024).decode('utf-8')
            print(response)
            
    except KeyboardInterrupt:
        print("Closing connection.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_loop()