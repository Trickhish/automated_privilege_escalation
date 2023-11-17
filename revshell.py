import socket
import threading

HOST = "127.0.0.1"
PORT = 1234

def handle_client(client_socket):
    # Receive and send data to/from the client
    while True:
        print("T")
        data = client_socket.recv(1024)
        if not data:
            break

        print(f"{client_socket.getpeername()}: {data.decode('utf-8')}")

        # Echo the received data back to the client

        #response = f"Server received: {data.decode('utf-8')}"
        #client_socket.send(response.encode('utf-8'))

    # Close the client socket when the communication is done
    print(f"Connection from {client_socket.getpeername()} closed.")
    client_socket.close()

def send_data_to_clients(clients, message):
    # Send the message to all connected clients
    for client_socket, _ in clients:
        try:
            client_socket.send(message.encode('utf-8'))
        except socket.error:
            # If the send operation fails, assume the client has disconnected
            continue

def start_server():
    global HOST
    global PORT
    
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((HOST, PORT))

    # Enable the server to accept connections
    server_socket.listen(5)
    print("Server listening on port 8888...")

    while True:
        # Accept a connection from a client
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        # Add the client to the list
        clients.append((client_socket, addr))

        # Create a new thread to handle the client
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def input_thread():
    # Allow the user to input messages to send to clients
    while True:
        message = input("Enter message to send to clients: ")
        send_data_to_clients(clients, message)
        
if __name__ == "__main__":
    # List to store connected clients
    clients = []

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the input thread
    input_thread = threading.Thread(target=input_thread)
    input_thread.start()

    # Wait for both threads to finish
    server_thread.join()
    input_thread.join()
