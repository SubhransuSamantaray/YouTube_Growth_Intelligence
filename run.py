"""
Entrypoint script to start the YouTube Channel Growth Intelligence Platform server.
"""
import uvicorn
import webbrowser
import os
import threading
import time

def open_browser(port):
    time.sleep(1.2)
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception as e:
        pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"\n========================================================")
    print(f" YouTube Channel Growth Intelligence Platform")
    print(f" Web Dashboard:  http://localhost:{port}")
    print(f" Interactive API: http://localhost:{port}/docs")
    print(f" Compliance:     30-Day TTL Sweeper Active (ToS III.E.4)")
    print(f"========================================================\n")
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
