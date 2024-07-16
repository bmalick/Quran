# send notifications

import os, re
from src.base import Base
import concurrent.futures

class SunnahCollection(Base):
    _base_url = "https://sunnah.com/"

    def __init__(self, name: str, url: str) -> None:
        super().__init__()
        self.save_parameters(name=name, url=url)
        self.get_books()
    
    def get_books(self):
        # soup = Base.get_soup(self.url)
        # collection_books = soup.find_all(name="div", attrs={"class": "book_title"})
        # books = []
        # futures = []
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     for book_item in collection_books:
        #         futures.append(executor.submit(self.get_book, book_item))
        #     for future in concurrent.futures.as_completed(futures):
        #         books.append(future.result())
        # books = sorted(books, key=lambda x: x.number)

        soup = Base.get_soup(self.url)
        book_item = soup.find(name="div", attrs={"class": "book_title"})
        books = [self.get_book(book_item)]
        self.save_parameters(books=books[:1]) #! change
    
    def get_book(self, item):
        book_url = self._base_url + item.find(name="a").attrs["href"]
        book_number = Base.get_item(item, "div.book_number")
        book_title = Base.get_item(item, "div.english_book_name")
        return Book(int(book_number), book_title, book_url, self.name)



class Book(Base):
    def __init__(self, number, title, url, collection: str) -> None:
        super().__init__()
        self.save_parameters(number=number, title=title,
                             url=url, collection=collection)
        self.get_chapters()
        self.save()
    
    def get_chapters(self):
        soup = self.get_soup(self.url)
        chapters = []
        for chapter in soup.find_all(name="div", attrs={"class": "chapter"}):
            next_sibling = chapter.find_next_sibling()
            hadiths = []
            chapter_num = chapter.find(name="div", attrs={"class": "echapno"}).get_text()
            chapter_title = chapter.find(name="div", attrs={"class": "englishchapter"}).get_text()
            chapter_title = chapter_title.replace("Chapter:", '')

            while next_sibling and next_sibling.get("class"):
                if "actualHadithContainer" in next_sibling.get("class"):
                    hadiths.append(next_sibling)
                next_sibling = next_sibling.find_next_sibling()
            chapters.append((chapter_num, chapter_title, [self.get_haddith(item) for item in hadiths]))

        self.save_parameters(chapters=chapters)
    
    def get_haddith(self, item):
        narrated_by = self.get_item(item, "div.hadith_narrated")
        content = self.get_item(item, "div.english_hadith_full > div.text_details")
        collection, book_reference = item.find("table", attrs={"class": "hadith_reference"}).find_all(name="tr")[:2]
        collection = collection.find(name="a").get_text().strip()
        book_reference = book_reference.find_all(name="td")[-1].get_text().replace(":", '').strip()
        return Haddith(collection, book_reference, narrated_by, content)
    
    def save(self):
        self.create_dir(self.collection)
        book_dir = os.path.join(self.collection, f"{self.number}")
        self.create_dir(book_dir)
        for chapter in self.chapters:
            content = "\n\n\n\n".join([haddith.content for haddith in chapter[-1]])
            with open(os.path.join(book_dir, f"{chapter[0][1:-1]}.txt"), 'w') as f:
                f.write(content)

class Haddith(Base):
    def __init__(self, collection, book_reference, narrated_by, content) -> None:
        super().__init__()
        self.save_parameters(book_reference=book_reference,
                             collection=collection,
                             narrated_by=narrated_by,
                             content=content)
        
        
    
    def get_text(self) -> str:
        text = "%(narrated_by)s\n%(content)s\n\n" % {
            "narrated_by": self.narrated_by,
            "content": re.sub(r"\s+", ' ', self.content).strip()
        }

        text += "%s: %s\n%s: %s" % (
            "Reference".ljust(10), self.collection,
            "Book".ljust(10), self.book_reference,

        )

        return text
