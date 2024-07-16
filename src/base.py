import requests, time, os
from bs4 import BeautifulSoup
from PIL import Image
import urllib.parse

class Parameters:
    def save_parameters(self, ignore: list[str] = None, **kwargs):
        ignore = ignore or []
        for k, v in kwargs.items():
            if k not in ignore: setattr(self, k, v)

class Base(Parameters):
    @staticmethod
    def get_soup(url: str) -> BeautifulSoup:
        try:
            response = requests.get(url=url)
        except requests.exceptions.RequestException as e:
            return None
        return BeautifulSoup(response.text, "html.parser")
    
    @staticmethod
    def get_item(soup, selector):
        item = soup.select_one(selector=selector)
        if item is not None:
            return item.get_text().strip()
        return
    @staticmethod
    def get_items(soup, selector):
        items = soup.select(selector=selector)
        if len(items)>0:
            return [item.get_text().strip() for item in items]
        return
    
    def create_dir(self, path: str): os.makedirs(path, exist_ok=True)
    
    # @staticmethod
    # def download_image(url: str, fname: str):
    #     response = requests.get(url, headers=Base.headers(url), stream=True)
    #     response.raise_for_status()
    #     if response.ok:
    #         with open(fname, "wb") as f:
    #             f.write(response.content)
    #     Base.convert2image(fname)
    
    # @staticmethod
    # def convert2image(fname: str) -> None:
    #     if fname.endswith(".webp"):
    #         img = Image.open(fname)
    #         img.save(fname.replace(".webp", ".jpg"), 'JPEG')
    #         os.remove(fname)
    
    # @staticmethod
    # def headers(url):
    #     return {
    #         'Accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) '
    #                       'Version/13.1.2 Safari/605.1.15',
    #         'Host': urllib.parse.urlparse(url).netloc, 'Accept-Language': 'en-ca', 'Referer': "https://manganato.com",
    #         'Connection': 'keep-alive'
    #     }

class Timer:
    def __init__(self, message: str = "") -> None:
        self.message = message
    
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.time()
        self.duration = self.end - self.start
        print("%s %.2f seconds" % (self.message, self.duration))


class Displayer(Parameters):

    def __init__(self, widths: list[int] = [4, 60], columns: list[str] = ['', "Title"]) -> None:
        assert len(widths) == len(columns), "widths and columns arguments must have the same number of elements."
        self.save_parameters(widths=widths, columns=columns)

    @property
    def line(self) -> str:
        line = "+" + "%s+" * len(self.widths)
        line %= tuple(['-'*w for w in self.widths])
        return line
    
    @property
    def top(self) -> str:
        res = self.line + "\n"
        cols = "|" + " %s|" * len(self.widths)
        cols %= tuple([col.ljust(w-1)
                       for w,col in zip(self.widths, self.columns)])
        res += cols
        res += "\n|%s|\n" % self.line[1:-1]
        return res   
    
    def display(self, to_display: list):
        text = self.top
        for idx, args in enumerate(to_display):
            col = "|" + " %s |" * len(self.widths) + "\n"
            col %= tuple([str(idx+1).ljust(self.widths[0]-2)] + [
                val.ljust(w-2) if isinstance(val, str) else str(val).rjust(w-2)
                for w,val in zip(self.widths[1:], args)
            ])
            text += col
        text += self.line
        return text