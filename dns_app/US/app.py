from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Missing required parameters", 400

    dns_query = (
        f"TYPE=A\n"
        f"NAME={hostname}"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    try:
        sock.sendto(dns_query.encode(), (as_ip, int(as_port)))
        data, _ = sock.recvfrom(1024)
    except (socket.timeout, ValueError):
        sock.close()
        return "Could not contact authoritative server", 400

    sock.close()

    dns_response = data.decode().strip()

    if dns_response == "Record not found":
        return "DNS record not found", 400

    fields = {}
    
    for item in dns_response.replace("\n", " ").split():
        if "=" in item:
            key, value = item.split("=", 1)
            fields[key] = value

    fs_ip = fields.get("VALUE")

    if not fs_ip:
        return "Invalid DNS response", 400

    try:
        response = requests.get(
            f"http://{fs_ip}:{fs_port}/fibonacci",
            params={"number": number},
            timeout=5
        )
    except requests.RequestException:
        return "Could not contact Fibonacci server", 400

    if response.status_code != 200:
        return response.text, response.status_code

    return jsonify(response.json()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)