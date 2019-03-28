from hyper import HTTPConnection
conn = HTTPConnection("tebigeek.com:443")  # try to upgrade HTTP2
conn.request('GET', '/get')  # GET command
resp = conn.get_response()

print("HTTP/2 found")

input("Press enter to exit ;)")
