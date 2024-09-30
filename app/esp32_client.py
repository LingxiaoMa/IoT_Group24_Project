import socket

# Function to send a message to the ESP32 via TCP
def send_message_to_esp32(message):
    esp32_ip = "172.20.10.5"  # Replace with the ESP32's IP address
    esp32_port = 5012           # Replace with the port ESP32 is listening on

    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the ESP32
        sock.connect((esp32_ip, esp32_port))
        print(f"Connected to ESP32 at {esp32_ip}:{esp32_port}")

        # Send the message to the ESP32
        sock.sendall((message + "\n").encode('utf-8'))  # Ensure message ends with a newline
        print(f"Sent message: {message}")

    except Exception as e:
        print(f"Error sending message to ESP32: {e}")
    finally:
        # Close the connection
        sock.close()
        print("Connection to ESP32 closed.")
