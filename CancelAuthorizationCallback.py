import http.server
import socketserver
import _thread

def RunServer() :
    HOST = 'localhost'
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        httpd.serve_forever()

def StartCallbackServerThread() :
    try:
        _thread.start_new_thread(RunServer)
    except:
        print("Error: unable to start thread")