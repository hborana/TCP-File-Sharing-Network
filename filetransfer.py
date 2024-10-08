from typing import BinaryIO
import socket
import sys
import os

def file_server(iface:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
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
       # sys.exit(1)

    if use_udp:
        try:
            while True:
                data, _address = _serverSocket.recvfrom(256)
                # if _message is None:
                #     break
                # print("Received message from", _address, "\n")
                if not data:
                    break
                fp.write(data)

        except Exception as e:
            print(e)
            _serverSocket.close()
            return
    
    # TCP server part 
    else: 
        try: 
            # start listening for client
            # 1, specifies the maximum number of queued connections
            _serverSocket.listen(1)

            # the server to continue accepting new connections as long as it's True
            _listening = True

            while _listening:
                _clientSocket, _address = _serverSocket.accept()

                while True:
                    data = _clientSocket.recv(256)
                    if not data:
                        _listening = False
                        break
                    fp.write(data)

        except Exception as e:
            print(e)
            _serverSocket.close()
            return
    return

def file_client(host:str, port:int, use_udp:bool, fp:BinaryIO) -> None:
    # pass
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

    #try:
            # Check if UDP is used
    if use_udp:
        try:
            while True:
                data = fp.read(256)
                if not data:
                    break
                _clientSocket.sendto(data,(host,port))
            _clientSocket.sendto(b"",(host,port))

        except Exception as e:
            print(e)
            _clientSocket.close()

    else:
        try:
            while True:
                data = fp.read(256)
                if not data:
                    break
                _clientSocket.send(data)
            _clientSocket.send(b"")

        except Exception as e:
            print(e)
            _clientSocket.close()

    # except Exception as e:
    #     print(e)

    # Close the client socket
    _clientSocket.close()
    sys.exit(0)   


 
