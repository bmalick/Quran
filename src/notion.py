
import requests, yaml
from src.surah import Surah
from typing import Union, List, Dict, Any

class Notion:
    _keys_fname = "keys.yaml"
    _config_fname = "config.yaml"
    _max_chars = 1999
    def __init__(self) -> None:
        self.get_keys()
        self.set_headers()

    def get_keys(self) -> None:
        with open(self._keys_fname, 'r') as file:
            self.data = yaml.safe_load(file)
    
    @property
    def config(self) -> Dict:
        with open(self._config_fname, 'r') as file:
            return yaml.safe_load(file)

    def set_headers(self) -> None:
        self.headers ={
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization": "Bearer %s" % self.data.get("api_token")
        }
    
    def create_surah(self, surah: Surah):
        num_split = len(surah.full_surah_translated) // self._max_chars
        translation = self.fill_object(
            "callout",
            ["Translation\n", "https://www.notion.so/icons/book_gray.svg", "default"]
        )
        for i in range(num_split+1):
            translation["callout"]["rich_text"].append({
                "type": "text", "text": {"content": surah.full_surah_translated[i*self._max_chars:(i+1)*self._max_chars]}
            })
        children = [translation]
        children.append(
            self.fill_object("heading_2", ["Surah info", "default", False])
        )
        for name, text in surah.info.items():
            if len(text)>0:
                num_split = len(text) // self._max_chars
                start = self.fill_object(
                    "callout",
                    [f"{name}\n", "https://www.notion.so/icons/book_gray.svg", "default"]
                )
                for i in range(num_split+1):
                    start["callout"]["rich_text"].append({
                        "type": "text", "text": {"content": text[i*self._max_chars:(i+1)*self._max_chars]}
                    })
                children.append(start)
        

        response = requests.post(
            url="https://api.notion.com/v1/pages",
            headers=self.headers,
            json={
                "parent": self.fill_object("parent", [self.data.get("database_id")]),
                "icon": self.fill_object("icon", ["https://www.notion.so/icons/book_gray.svg"]),
                "properties": {
                    "Name": self.fill_object("page_title", [surah.name]),
                    "Number": self.fill_object("number", [surah.number]),
                    "URL": self.fill_object("url", [surah.url]),
                    "Audio": self.fill_object("url", [surah.audio_url]),
                    "Total ayahs": self.fill_object("number", [surah.num_ayahs]),
                    "Ayah": self.fill_object("number", [0]),
                },
                "children": children
                # "children": [
                #     self.fill_object("callout",
                #                      ["Translation", "\n" + surah.full_surah_translated[:1999],
                #                       "https://www.notion.so/icons/book_gray.svg", "default"]),
                    
                # ] + [
                #     # self.fill_object(
                #     #     "callout",
                #     #     [key, "\n" + value[:self._max_chars], "https://www.notion.so/icons/book_gray.svg", "default"]
                #     # )
                #     # for key, value in surah.info.items()
                #     # if len(value)>0
                # ]
            }
        )
        try:
            response.raise_for_status()
        except:
            print(response.text)
    
    def fill_object(self, property_object: str, property_values: List[Any]) -> Dict:
        assert isinstance(property_values, list), "Enter a list please."
        args = self.config["objects"][property_object].copy()
        item = args["object"].copy()
        for path, value in zip(args["paths"], property_values):
            item = self.update_from_path(item, path, value).copy()
        return item
    
    @staticmethod
    def update_from_path(dictionnary: Dict, path: str, value: Union[str, List]) -> Dict:
        keys = path.split('.')
        current = dictionnary
        for key in keys[:-1]:
            if '[' in key:
                key_split = key.split('[')
                key = key_split[0]
                idx = int(key_split[1][:-1])
                try:
                    current = current[key][idx]
                except:
                    current = current[key]
                    current.append({})
                    current = current[-1]
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
        current[keys[-1]] = value
        return dictionnary


    # def fill_block()

