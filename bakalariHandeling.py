import requests
import pybakalib

#client = pybakalib.client.BakaClient(url)

class Client:
    def set_url(self, url):
        self.url = url
        self.client = pybakalib.client.BakaClient(url)
    def login(self, username, password):
        self.client.login(username, password)
    def get_rozvrh(self,date):
        return requests.get(f"{self.url}/login.aspx", params={"hx":self.client.token, "pm":"rozvrh","pmd":date}).text
