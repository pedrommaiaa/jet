import time
import socket
from .utils import read_response, server

def test_ping_response(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        client.sendall(b"*1\r\n$4\r\nPING\r\n")
        response = read_response(client, b"+PONG\r\n")
        assert response == b"+PONG\r\n", f"Expected '+PONG\\r\\n', got '{response.decode()}'"
    finally:
        client.close()

def test_multiple_ping_response(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        client.sendall(b"*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n")
        response = read_response(client, b"+PONG\r\n+PONG\r\n")
        assert response == b"+PONG\r\n+PONG\r\n", f"Expected '+PONG\\r\\n+PONG\\r\\n', got '{response.decode()}'"
    finally:
        client.close()

def test_echo_response(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        message = b"Hello, World!"
        message_length = len(message)
        client.sendall(b"*2\r\n$4\r\nECHO\r\n$" + str(message_length).encode() + b"\r\n" + message + b"\r\n")
        expected_response = b"$" + str(message_length).encode() + b"\r\n" + message + b"\r\n"
        response = read_response(client, expected_response)
        assert response == expected_response, f"Expected '{expected_response.decode()}', got '{response.decode()}'"
    finally:
        client.close()

def test_set_response(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        # Sending SET command to store the value 'World' at key 'Hello'
        client.sendall(b"*3\r\n$3\r\nSET\r\n$5\r\nHello\r\n$5\r\nWorld\r\n")
        response = read_response(client, b"+OK\r\n")
        assert response == b"+OK\r\n", f"Expected '+OK\\r\\n', got '{response.decode()}'"
    finally:
        client.close()

def test_set_with_expiry(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        # Set the value 'temp' at key 'expire_key' with an expiry of 1000 milliseconds (1 second)
        client.sendall(b"*5\r\n$3\r\nSET\r\n$10\r\nexpire_key\r\n$4\r\ntemp\r\n$2\r\nPX\r\n$4\r\n1000\r\n")
        set_response = read_response(client, b"+OK\r\n")
        assert set_response == b"+OK\r\n", f"Expected '+OK\\r\\n' after SET with expiry, got '{set_response.decode()}'"

        # Sleep for a duration longer than the expiry time to ensure the key has expired
        time.sleep(1.5)  # Sleep for 1.5 seconds to ensure expiry has passed

        # Attempt to get the value of 'expire_key', expecting it to have expired
        client.sendall(b"*2\r\n$3\r\nGET\r\n$10\r\nexpire_key\r\n")
        expected_get_response = b"$-1\r\n"  # This is the response when the key does not exist
        get_response = read_response(client, expected_get_response)
        assert get_response == expected_get_response, f"Expected '{expected_get_response.decode()}' for expired key, got '{get_response.decode()}'"
    finally:
        client.close()

def test_get_response(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6379))
    try:
        # First, set the value 'World' at key 'Hello'
        client.sendall(b"*3\r\n$3\r\nSET\r\n$5\r\nHello\r\n$5\r\nWorld\r\n")
        # Wait for the OK response from the SET command
        set_response = read_response(client, b"+OK\r\n")
        assert set_response == b"+OK\r\n", f"Expected '+OK\\r\\n' after SET, got '{set_response.decode()}'"

        # Then, retrieve the value 'World' at key 'Hello'
        client.sendall(b"*2\r\n$3\r\nGET\r\n$5\r\nHello\r\n")
        expected_get_response = b"$5\r\nWorld\r\n"
        get_response = read_response(client, expected_get_response)
        assert get_response == expected_get_response, f"Expected '{expected_get_response.decode()}', got '{get_response.decode()}'"
    finally:
        client.close()
