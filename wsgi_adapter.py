from flask import Flask, request, Response
import requests
import threading
import uvicorn
import time
import os

app = Flask(__name__)

# Get host and port for FastAPI
FASTAPI_HOST = "127.0.0.1"  # Use local host for internal communication
FASTAPI_PORT = 8000  # Different port to avoid conflict

def start_fastapi():
    """Start FastAPI server in a separate thread"""
    import uvicorn
    from main import app as fastapi_app
    uvicorn.run(fastapi_app, host=FASTAPI_HOST, port=FASTAPI_PORT)

# Start FastAPI server in a separate thread
fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
fastapi_thread.start()
# Give FastAPI time to start
time.sleep(2)
print(f"FastAPI running on http://{FASTAPI_HOST}:{FASTAPI_PORT}")

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    # Forward the request to FastAPI
    fastapi_url = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}/{path}"
    
    # Get the request method
    method = request.method
    
    # Get request headers
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    # Get request data/form/files
    data = request.get_data()
    
    # Make the request to FastAPI
    try:
        resp = requests.request(
            method=method,
            url=fastapi_url,
            headers=headers,
            data=data,
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Create Flask response from FastAPI response
        response = Response(
            resp.iter_content(chunk_size=10*1024),
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'text/html')
        )
        
        # Copy FastAPI response headers to Flask response
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'connection', 'content-encoding'):
                response.headers[key] = value
                
        return response
    except requests.exceptions.RequestException as e:
        return f"Error forwarding request to FastAPI: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)