import requests

# Basic auth class for PorductsUp


class ProductUpAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = f"{client_id}:{client_secret}"

    def get_headers(self):
        return {"X-Auth-Token": self.token}

    def make_request(self, url):
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response.json()


if __name__ == '__main__':
    auth = ProductUpAuth("1234", "simsalabim")
    response = auth.make_request("https://platform-api.productsup.io/")
