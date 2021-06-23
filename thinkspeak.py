import socket

URL = "86.217.14.104"
#
# fields : [string]
# otherParams : {name: data}
#
def post_thingspeak(api_key, fields = [], otherParams = {}):
    
    addr = socket.getaddrinfo(URL, 443)[0][-1]
    s = socket.socket()
    s.connect(addr)
    
    params = ""
    first = False
    for i, e in enumerate(fields):
        if not first:
            first = True
        else:
            params = params + "&"
        params = params + "field{}={}".format(i+1, str(e, 'utf8'))
    
    for name, data in otherParams:
        if not first:
            first = True
        else:
            params = params + "&"
        params = params + "{}={}".format(name, data)
    
    post_data = 'POST /update HTTP/1.1\r\nHost: {}:443\r\nConnection: close\r\nX-THINGSPEAKAPIKEY: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}'.format(URL, api_key, str(len(params)), params)
    
    s.send(bytes(post_data, 'utf8'))
    s.close()

def get_thingspeak(channel):
    
    addr = socket.getaddrinfo(URL, 443)[0][-1]
    s = socket.socket()
    s.connect(addr)
    
    get = 'GET /channels/{}/feeds/last HTTP/1.1\r\nHost: {}\r\n\r\n'.format(channel, URL)
    
    s.send(bytes(get, 'utf8'))

    ret = ""
    
    while True:
        data = s.recv(584)
        data = s.recv(250)
        if data:
            s.close()
            return str(data, 'utf8')
        else:
            break