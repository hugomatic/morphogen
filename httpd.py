import os
from time import time
from stlfacets import facets_from_file
try:
    from  http.server import HTTPServer as C_server
    from  http.server import BaseHTTPRequestHandler as C_base_handler
    from  http.server import SimpleHTTPRequestHandler as C_simple_handler
    print("Python 3.2!")
except:
    from BaseHTTPServer import HTTPServer as C_server
    from BaseHTTPServer import BaseHTTPRequestHandler as C_base_handler
    from SimpleHTTPServer import SimpleHTTPRequestHandler as C_simple_handler
    print("Python 2.7!")
    

def run(port, server_class=C_server, handler_class=C_base_handler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

    
    
def add_facet_event(s, p0, p1, p2):
    s.wfile.write("event: facet\n".encode('utf-8'))
    s.wfile.write(('data: {"a":[%.4f, %.4f, %.4f], "b":[%.4f, %.4f, %.4f], "c":[%.4f, %.4f, %.4f]}\n' % (p0[0],p0[1],p0[2],p1[0],p1[1],p1[2],p2[0],p2[1],p2[2] )).encode('utf-8'))
    s.wfile.write("\n".encode('utf-8'))


def stream_mesh_file(s, filename):
    print("streaming mesh")
    print("  opening %s" % filename)
    s.send_response(200)
    s.send_header("Content-type", "text/event-stream")
    s.end_headers()
 
    start_time = time()
    facet_generator = facets_from_file(filename)
    
    i = 0
    try:
        while 1:
            i += 1;
            normal, v0,v1,v2  = next(facet_generator)
            add_facet_event(s, v0,v1,v2) 
            
    except StopIteration:
        pass
    
        
    print("  done")
    s.wfile.write("event: done\n".encode('utf-8'))
    s.wfile.write(("data: %s\n" % s.path ).encode('utf-8'))
    s.wfile.write("\n".encode('utf-8'))
    
    print("  %d facets" % i)
    elapsed = time() - start_time
    print ("  File read in %s sec" % (elapsed) )        
    

class MeshStreamer(C_simple_handler):
    
    def do_GET(s):
        print(s.path)
        if  s.path.lower().endswith(".stl"):
            filename = "." + s.path
            if os.path.exists(filename):
                stream_mesh_file(s, filename)
                return
            
        # if we get here, we didn't get an stl file to stream
        # call the parent's get 
        C_simple_handler.do_GET(s)
        
port = 8000
print("Running at PORT: %s" % port)    
run(port, handler_class=MeshStreamer)
