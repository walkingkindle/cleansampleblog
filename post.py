import requests
class Post:
    def __int__(self):
        url="https://api.npoint.io/93f14c94fb7ca980d04a"
        self.response = requests.get(url=url).json()
        title1 = self.response[0]['title']
        subtitle1 = self.response[0]['subtitle']
