# import libraries , which are necessary for the code  

import socket
import sys
import os
import threading


# Lets create empty list  to manage all the CLIENTS 

clients = []

# LEts create a function to mangage Threads 
def _manageThreads(_serverSocket, serverEvent):
        while True:
            if serverEvent.is_set():
                # Close all client connections gracefully
                for hb_c in clients:
                    if hb_c:
                        try:
                            hb_c.close()
                        except Exception as e:
                            print(f"Error while closing client connection: {e}")

                # Close the server socket gracefully
                try:
                    _serverSocket.close()
                except Exception as e:
                    print(f"Error while closing server socket: {e}")

                # Exit the loop and thread
                break
                
def manageClients(_serverSocket, _clientSocket, _address, serverEvent):
    try:
        while True:
            if serverEvent.is_set():
                # testing whether is_set event it working or not ?
                _serverSocket.close()
                _clientSocket.close()
                break
            
            # Receive message from the client
            _message = _clientSocket.recv(256)
            if not _message:
                # No data received, client disconnected
                _clientSocket.close()
                break

            print("Received message from", _address)    

            # Decode the received message from bytes to a string and remove leading/trailing whitespace
            _message = _message.decode().strip()
            response = _message

            # Setting the response based on the received message
            if _message == "hello":
                response = "world\n"
            elif _message == "goodbye":
                response = "farewell"
            elif _message == "exit":
                response = "ok"

            #if _message == "exit":
                if len(clients) == 1:
                    serverEvent.set()

            # Encode the response as UTF-8 bytes
            response = response.encode("utf-8")

            # Send the response back to the client
            _clientSocket.send(response)

            if _message in ["exit", "goodbye"]:
                # Close the client socket if necessary
                _clientSocket.close()
                # if _message == "exit":
                #     if len(clients) == 1:
                #       serverEvent.set()

            
                break

    except Exception as e:
         print("Error:", e)
   # finally:    # Ensure the clientSocket is removed from CLIENTS list
    if _clientSocket in clients:
        clients.remove(_clientSocket)

def chat_server(iface: str, port: int, use_udp: bool) -> None:
    print("Hello, I am a server\n")


    # Determine the socket type based on the use_udp flag
    socket_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM

    # Get address information with AF_UNSPEC and the determined socket type
    socket_info = socket.getaddrinfo(iface, port, socket.AF_UNSPEC, socket_type)
    family, _socketType, protocolType, canonname, socketAddress = socket_info[0]

    try:
        # Continue with the rest server setup using the extracted information
        _serverSocket = socket.socket(family, _socketType, protocolType)
        _serverSocket.bind(socketAddress)

    except (socket.gaierror, IndexError) as e:
        print(e)
        # if '_serverSocket' in locals():
        _serverSocket.close()
        return

    if port < 1024:
        _serverSocket.close()
        sys.exit(1)

    if use_udp:
        try:
            while True:
                _message, _address = _serverSocket.recvfrom(256)
                if _message is None:
                    break
                print("Received message from", _address, "\n")

                _message = _message.decode("utf-8").strip()
                response = _message
                if _message == "hello":
                    response = "world\n"
                if _message == "goodbye":
                    response = "farewell"
                if _message == "exit":
                    response == "ok"
                response = response.encode("utf-8")
                _serverSocket.sendto(response, _address)

                if _message == "exit":
                    _serverSocket.close()
                    return

                elif _message == "goodbye":
                    break
        
        except Exception as e:
            print(e)
            _serverSocket.close()
            return
    # TCP server part 
    else: 
        try: 
            # start listening for incoming connections 
            _serverSocket.listen()

            #Create an event to manage server shutdown
            serverEvent = threading.Event()

            # Create a sepearte thread to handle server shutdown
            new_TEvent = threading.Thread(target=lambda: _manageThreads(_serverSocket,serverEvent))

            # Set the new thread as a Daemon thread to all0w sm00th program termination
            new_TEvent.daemon = True
            new_TEvent.start()

            no_ofClients = 0

            while not serverEvent.is_set():
                # Accept a new client connection
                client, _address = _serverSocket.accept()

                # Add the client socket to the list of clients
                clients.append(client)

                # Print information about the new connection
                print("New Client :- ", no_ofClients, "from :", _address, "\n")
                no_ofClients += 1

                # Start a new thread to manage the client
                New_clientT = threading.Thread(
                    target=manageClients,
                    args=(_serverSocket, client, _address, serverEvent),
                )

                # Set the client thread as a daemon to allow program termination
                New_clientT.daemon = True
                New_clientT.start()
        except Exception as e:
            print(e)
            return
    return

# CLient function :--
def chat_client(host: str, port: int, use_udp: bool) -> None:
    print("Hello, I am client")

     # Determine the socket type based on the use_udp flag
    socket_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM

    # Get address information with AF_UNSPEC and the determined socket type
    socket_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket_type)
    family, _socketType, protocolType, canonname, socketAddress = socket_info[0]

    try:
        # Continue with the rest of client connection
        _clientSocket = socket.socket(family, _socketType, protocolType)
        _clientSocket.connect(socketAddress)

    except (socket.gaierror, IndexError) as e:
        print(e)
        # if '_clientSocket' in locals():
        _clientSocket.close()
        sys.exit(1)

    if port < 1024:
        _clientSocket.close()
        sys.exit(1) 

    while True:
         # Read user input
        _message = input()
        try:
            # Check if UDP is used
            if use_udp:
                 # Send the message as bytes over UDP
                _clientSocket.sendto(_message.encode("utf-8"), (host, port))
                 # Receive response and sender's address
                response, _address = _clientSocket.recvfrom(256)

            else:
                # Send the message as bytes over TCP
                _clientSocket.send(_message.encode("utf-8"))
                 # Receive response from the server
                response = _clientSocket.recv(256)

             # Check if the response is empty
            if not response:
                break

            # Decode the response from bytes to a string
            response = response.decode()
            print(response)

            # Check if the user input indicates an exit
            if _message in ["exit","goodbye"]:
                break

        except Exception as e:
            print(e)
            break
    # Close the client socket
    _clientSocket.close()
    sys.exit(0)   

