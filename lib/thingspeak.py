import socket

URL = "86.217.14.104"
#
# fields : [string]
# otherParams : {name: data}
#
def post_thingspeak(api_key, fields = [], otherParams = {}, proxy = None, proxy_port = 443):
    
    s = None
    
    if proxy == None:
        s = http_proxy_connect(socket.getaddrinfo(URL, 443)[0][-1])
    else:
        s = http_proxy_connect(socket.getaddrinfo(URL, 443)[0][-1], socket.getaddrinfo(proxy, proxy_port)[0][-1])
    
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

def get_thingspeak(channel, proxy = None, proxy_port = 443):
    
    s = None
    
    if proxy == None:
        s = http_proxy_connect(socket.getaddrinfo(URL, 443)[0][-1])
    else:
        s = http_proxy_connect(socket.getaddrinfo(URL, 443)[0][-1], socket.getaddrinfo(proxy, proxy_port)[0][-1])
    
    get = 'GET /channels/{}/feeds/last HTTP/1.1\r\nHost: {}:443\r\n\r\n'.format(channel, URL)
    
    s.send(bytes(get, 'utf8'))

    data = ""
    
    current = s.readline()
    while not (not current):
        data = current
        current = s.readline()
    s.close()
    return str(data, 'utf-8')


def http_proxy_connect(address, proxy = None):
    """
  Establish a socket connection through an HTTP proxy.
  
  Arguments:
    address (required)     = The address of the target
    proxy (def: None)      = The address of the proxy server
    headers (def: {})      = A set of headers that will be sent to the proxy
  
  Returns:
    a socket
    """
    if proxy == None:
        s = socket.socket()
        s.connect(address)
        return s
  
    headers = {
        'host': address[0]
    }
    s = socket.socket()
    s.connect(proxy)
    
    s.send('CONNECT {0}:{1} HTTP/1.0\r\nHost: {0}:{1}\r\n\r\n'.format(address[0], address[1]))
    
    statusline = str(s.readline(), "utf-8")
    
    if statusline.count(' ') < 2:
        s.close()
        raise IOError('Bad response')
    
    version, status, statusmsg = statusline.split(' ', 2)
    
    if not version in ('HTTP/1.0', 'HTTP/1.1'):
        s.close()
        raise IOError('Unsupported HTTP version')
    
    try:
        status = int(status)
    except ValueError:
        s.close()
        raise IOError('Bad response')
  
    response_headers = {}
    
    return s