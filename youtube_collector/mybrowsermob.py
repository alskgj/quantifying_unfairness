import requests


class Server:

    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.browsermob_port = port
        self.BASE_URL = f'http://{self.host}:{self.browsermob_port}'

        print('active proxies:', requests.get(f'{self.BASE_URL}/proxy').text)
        self.cleanup()

        response = requests.post(f'{self.BASE_URL}/proxy', {'trustAllServers': True})  # todo trustAllServers?
        resp = response.json()
        self.port = resp['port']

    def cleanup(self):
        actives = requests.get(f'{self.BASE_URL}/proxy').json()
        for element in actives['proxyList']:
            print(f'shutting down proxy {element}')
            requests.delete(f'{self.BASE_URL}/{element["port"]}')

    def limit(self, amount):
        print(requests.put(f'{self.BASE_URL}/proxy/{self.port}/limit'), {
            'downstreamKbps': amount,
            'upstreamKbps': amount
        })

    def proxy_string(self):
        return f'127.0.0.1:{self.port}'


if __name__ == '__main__':
    server = Server()
    server.limit(10)
    print(server.proxy_string())

