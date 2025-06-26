from socket import *
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from httpserver import HttpServer

httpserver = HttpServer()

#untuk menggunakan threadpool executor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection, address):
    try:
        headers_data = b""
        while b"\r\n\r\n" not in headers_data:
            part = connection.recv(1024)
            if not part:
                break
            headers_data += part

        header_text, _, rest_of_data = headers_data.partition(b"\r\n\r\n")
        header_text = header_text.decode('utf-8', errors='ignore')
        
        content_length = 0
        try:
            cl_header = [line for line in header_text.split('\r\n') if 'content-length' in line.lower()]
            if cl_header:
                content_length = int(cl_header[0].split(':')[1].strip())
        except (ValueError, IndexError):
            pass

        body_data = rest_of_data
        while len(body_data) < content_length:
            part = connection.recv(content_length - len(body_data))
            if not part:
                break
            body_data += part

        full_request = header_text + "\r\n\r\n" + body_data.decode('latin-1')

        hasil = httpserver.proses(full_request)
        
        connection.sendall(hasil)
    except Exception as e:
        logging.error(f"Error processing client {address}: {e}")
    finally:
        connection.close()



def Server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = 8885
    my_socket.bind(('0.0.0.0', port))
    my_socket.listen(1)
    logging.warning(f"Thread Pool Server running on port {port}")

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            executor.submit(ProcessTheClient, connection, client_address)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    Server()