import os
import time
import threading
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# Configurable backend ports (can be overridden by environment variables)
BACKENDS = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

# Thread safety lock for active_backends list
backends_lock = threading.Lock()
active_backends = list(BACKENDS)
current_index = 0

def run_health_checks():
    """Periodically check the health of each backend server to keep active_backends updated."""
    global active_backends
    print("[Health Checker] Started background check daemon.")
    while True:
        healthy = []
        for backend in BACKENDS:
            try:
                # Ping the root path of the backend with a short timeout
                resp = requests.get(backend, timeout=2.0)
                # Any status code less than 500 indicates the server is up and responsive
                if resp.status_code < 500:
                    healthy.append(backend)
            except requests.exceptions.RequestException:
                pass
        
        with backends_lock:
            active_backends = healthy
            
        time.sleep(5)  # Re-check every 5 seconds

# Start health checker as a daemon thread
checker_thread = threading.Thread(target=run_health_checks, daemon=True)
checker_thread.start()

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def load_balancer_proxy(path):
    global current_index
    
    with backends_lock:
        healthy_servers = list(active_backends)
        
    if not healthy_servers:
        return Response(
            "Service Temporarily Unavailable - No healthy backend server instances found.",
            status=503,
            content_type="text/plain"
        )
        
    # Get backend under round-robin
    backend = healthy_servers[current_index % len(healthy_servers)]
    current_index = (current_index + 1) % len(healthy_servers)
    
    # Construct destination URL
    url = f"{backend}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode('utf-8')}"
        
    # Prepare headers to forward (filtering hop-by-hop headers to prevent connection errors)
    excluded_headers = {'host', 'content-length', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'}
    headers = {key: value for key, value in request.headers.items() if key.lower() not in excluded_headers}
    
    try:
        # Proxy request to chosen backend
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Prepare response headers to forward back to client
        resp_headers = [
            (key, value) for key, value in resp.headers.items()
            if key.lower() not in excluded_headers
        ]
        
        return Response(
            resp.iter_content(chunk_size=4096),
            status=resp.status_code,
            headers=resp_headers
        )
        
    except requests.exceptions.RequestException as e:
        # If the request fails, remove it from active backends immediately and retry once on another server
        print(f"[Load Balancer] Failed to connect to backend {backend}: {e}")
        with backends_lock:
            if backend in active_backends:
                active_backends.remove(backend)
        return Response(
            f"Bad Gateway - Connection to backend instance {backend} failed.",
            status=502,
            content_type="text/plain"
        )

if __name__ == '__main__':
    # Load balancer listens on port 5000 by default
    port = int(os.environ.get('PORT', 5000))
    print(f"============================================================")
    print(f"CodeNative Load Balancer initialized on http://127.0.0.1:{port}")
    print(f"Distributing requests across: {', '.join(BACKENDS)}")
    print(f"============================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
