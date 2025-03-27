import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Print debugging information
            print(f"\nReceived request for path: {self.path}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Parse the URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # If accessing root or any path without extension
            if path == "/" or path == "":
                self.path = "/index.html"
                print(f"Redirecting to: {self.path}")
            else:
                # Set self.path to just the path component, ignoring query string
                self.path = path
                print(f"Using path without query string: {self.path}")
            
            # Get the full file path
            file_path = os.path.join(os.getcwd(), self.path.lstrip('/'))
            print(f"Looking for file at: {file_path}")
            
            # Check if file exists
            if os.path.exists(file_path):
                print(f"File found: {file_path}")
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
            else:
                print(f"File not found: {file_path}")
                # If the file doesn't exist and it's a route without extension, try serving index.html
                if '.' not in path.split('/')[-1]:
                    self.path = "/index.html"
                    print(f"Trying index.html instead: {self.path}")
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
                self.send_error(404, f"File not found: {self.path}")
                
        except Exception as e:
            print(f"Error handling request: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server():
    # Get the absolute path to the frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nStarting server...")
    print(f"Frontend directory: {frontend_dir}")
    
    # Change to the frontend directory
    os.chdir(frontend_dir)
    print(f"Changed working directory to: {os.getcwd()}")
    
    # List files in the directory
    print("\nFiles in directory:")
    for file in os.listdir():
        print(f"- {file}")
    
    # Configure and start the server
    PORT = 8000
    Handler = CustomHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\nServer is running!")
            print(f"Local URL: http://localhost:{PORT}")
            print(f"Network URL: http://192.168.1.4:{PORT}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        httpd.server_close()
    except Exception as e:
        print(f"\nError starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_server() 