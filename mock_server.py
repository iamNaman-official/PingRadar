import asyncio
import handlers
from router import get_handler

HOST = "127.0.0.1"
PORT = 8080

COUNT_REQUESTS = 0
COUNT_CONNECTIONS = 0
CONNECTION_STATS = {}


async def send_response(writer, status_code, body):
    """
    Sends a valid HTTP response.
    """

    status_messages = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        408: "Request Timeout",
        500: "Internal Server Error",
    }

    status_text = status_messages.get(
        status_code,
        "Unknown"
    )

    response = (
        f"HTTP/1.1 {status_code} {status_text}\r\n"
        "Content-Type: text/plain\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        "Connection: keep-alive\r\n"
        "\r\n"
        f"{body}"
    )

    writer.write(response.encode())
    await writer.drain()


async def handle_connection(reader, writer):
    """
    Handles one TCP connection.
    A single connection can receive
    multiple HTTP requests because
    of keep-alive.
    """

    global COUNT_CONNECTIONS
    global COUNT_REQUESTS


    COUNT_CONNECTIONS += 1
    connection_id = COUNT_CONNECTIONS
    CONNECTION_STATS[connection_id] = 0

    client_address = writer.get_extra_info("peername")
    print(
        f"New Connection #{connection_id} "
        f"{client_address}"
    )

    try:
        while True:
            request = await reader.read(1024)

            if not request:
                break

            COUNT_REQUESTS += 1
            CONNECTION_STATS[connection_id] += 1

            print(
                f"Connection #{connection_id} "
                f"handled Request #{COUNT_REQUESTS}"
            )
            request_text = request.decode()

            print("\n========== Incoming Request ==========")
            print(request_text)

            # Parse request line
            try:
                first_line = request_text.splitlines()[0]
                method, path, version = first_line.split()
                print(
                    f"Parsed Request - "
                    f"Method: {method}, "
                    f"Path: {path}, "
                    f"Version: {version}"
                )
            except ValueError:
                await send_response(
                    writer,
                    400,
                    "Bad Request"
                )
                continue

            print(f"Method  : {method}")
            print(f"Path    : {path}")
            print(f"Version : {version}")

            # -----------------------------
            # Routing
            # -----------------------------

            handler = get_handler(path)
            status, response_body = await handler()
            await send_response(writer, status, response_body)

    except Exception as e:
        print(f"Server Error: {e}")

    finally:
        print(f"Closing connection "f"{client_address[0]}:{client_address[1]}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_connection,
        HOST,
        PORT
    )

    print("=" * 50)
    print(f"Mock server running on http://{HOST}:{PORT}")
    print("=" * 50)

    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down...")

def print_statistics():
    print("\n" + "=" * 50)
    print("Server Statistics")
    print("=" * 50)
    print(f"Total Connections Created : {COUNT_CONNECTIONS}")
    print(f"Total Requests Served     : {COUNT_REQUESTS}")
    print("\nRequests Per Connection:")
    for connection_id, requests in CONNECTION_STATS.items():
        print(
            f"Connection #{connection_id} -> {requests} requests")

    print("=" * 50)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        print_statistics()