import socket
import os

HOST = "0.0.0.0"
PORT = 53533
RECORD_FILE = "dns_records.txt"


def save_record(name, value, record_type="A", ttl="10"):
    with open(RECORD_FILE, "a") as file:
        file.write(f"TYPE={record_type}\n")
        file.write(f"NAME={name}\n")
        file.write(f"VALUE={value}\n")
        file.write(f"TTL={ttl}\n\n")


def find_record(name):
    if not os.path.exists(RECORD_FILE):
        return None

    with open(RECORD_FILE, "r") as file:
        records = file.read().strip().split("\n\n")

    for record in reversed(records):
        fields = {}

        for line in record.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value

        if fields.get("NAME") == name and fields.get("TYPE") == "A":
            return fields

    return None


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"AS listening on UDP port {PORT}")

while True:
    data, address = server_socket.recvfrom(1024)
    message = data.decode().strip()

    fields = {}

    for line in message.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value

    # Registration message
    if "VALUE" in fields:
        save_record(
            fields.get("NAME"),
            fields.get("VALUE"),
            fields.get("TYPE", "A"),
            fields.get("TTL", "10")
        )

        server_socket.sendto(b"Registration successful", address)

    else:
        record = find_record(fields.get("NAME"))

        if record:
            response = (
                f"TYPE={record['TYPE']}\n"
                f"NAME={record['NAME']}\n"
                f"VALUE={record['VALUE']}\n"
                f"TTL={record['TTL']}"
            )
        else:
            response = "Record not found"

        server_socket.sendto(response.encode(), address)