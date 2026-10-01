from flask import Flask, request, jsonify
import socket

app = Flask(__name__)


def fibonacci(n):
    if n < 0:
        return None
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1

    for _ in range(2, n + 1):
        a, b = b, a + b

    return b


@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json()

    if not data:
        return "Missing JSON data", 400

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return "Missing required fields", 400

    message = (
    f"TYPE=A\n"
    f"NAME={hostname} VALUE={ip} TTL=10\n"
)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (as_ip, int(as_port)))
    sock.close()

    return "Registration successful", 201


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    number = request.args.get("number")

    try:
        number = int(number)
    except (TypeError, ValueError):
        return "Number must be an integer", 400

    result = fibonacci(number)

    if result is None:
        return "Number must be non-negative", 400

    return jsonify({"fibonacci": result}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)