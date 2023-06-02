import time
def app(environ, start_response):
    #Change the hostname to the hostname of the machine where docker runs
    HOSTNAME = "[CHANGE ME!]"
    with open("pipe", "w", encoding="utf-8") as f:
	    f.write("wake up\n")
    status = '307 Temporary Redirect'
    headers = [
             ("Location", f"http://{HOSTNAME}:8080/")]
    start_response(status, headers)
    return iter([b''])
