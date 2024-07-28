import requests


__publicKey__ = "pk_iAowuatam2AFNR3L"
__secretKey__ = "sk_VCGkbbNr9I5LBfdO"


class ShortioLinkGenerator:
    def __init__(self):
        self.api_key = __secretKey__
        self.base_url = 'https://api.short.io'
        self.domain = "ashbot.link"
        self.links_endpoint = '/links'
        self.headers = {
            'authorization': self.api_key,
            'content-type': 'application/json'
        }

    def shorten_link(self, original_url):
        payload = {
            'domain': self.domain,
            'originalURL': original_url
        }
        try:
            response = requests.post(
                f'{self.base_url}{self.links_endpoint}',
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_link(self, link_id):
        url = f'{self.base_url}/links/{link_id}'
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
