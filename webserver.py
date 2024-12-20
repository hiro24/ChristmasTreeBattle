import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import argparse

def start_server(directory, port):
    # Change the current working directory to the specified directory
    os.chdir(directory)

    # Set up the HTTP server
    server_address = ('', port)
    handler_class = SimpleHTTPRequestHandler
    httpd = HTTPServer(server_address, handler_class)

    print(f"Serving '{directory}' on port {port}. Press Ctrl+C to stop.")

    try:
        # Start the server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a simple HTTP server.")
    parser.add_argument(
        "-p", "--port", 
        type=int, 
        default=8000, 
        help="The port to serve on (default is 8000).",
    )

    args = parser.parse_args()

    directory = os.path.join(os.getcwd(), "html")

    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
    else:
        start_server(directory, args.port)

