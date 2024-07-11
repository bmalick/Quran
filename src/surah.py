from src.base import Base
import concurrent.futures

class Surah(Base):
    _base_url = "https://quran.com/"
    _surah_base_url = "https://quran.com/surah/%s/info"
    _audio_base_url = "https://download.quranicaudio.com/quran/sa3d_al-ghaamidi/complete/%s.mp3"
    def __init__(self, number: str, name: str = None,
                 translated_name: str = None):
        super().__init__()
        self.save_parameters(number=number,
                             name=name,
                             translated_name=translated_name,
                             url=self._base_url+str(number),
                             audio_url = self._audio_base_url % number)
        self.get_surah_info()
        self.get_ayahs()
        self.get_full_surah()
            
    def __str__(self): pass

    def get_surah_info(self) -> None:
        soup = self.get_soup(self._surah_base_url % self.number)
        header = soup.select_one("div.Info_surahName__X8hE6")
        surah_name = header.contents[-1]
        num_ayahs = header.next_sibling.find("p").next_sibling.get_text()
        revelation_place = header.next_sibling.find("div").next_sibling.find("p").next_sibling.get_text()
        
        if self.name is None:
            self.name = surah_name


        soup = soup.select_one("div.Info_textBody__Tx5BZ")
        note = soup.find(name="h2").find_previous_sibling()
        
        if note is not None:
            note = note.get_text()
        else: note = ''

        surah_info = {"note": note}
        for title in soup.find_all(name="h2"):
            next_sibling = title.find_next_sibling()
            paragraphs = []
            while next_sibling and next_sibling.name != 'h2':
                if next_sibling.name == 'p':
                    paragraphs.append(next_sibling.text)
                next_sibling = next_sibling.find_next_sibling()
            surah_info[title.get_text().strip()] = "\n".join(paragraphs)

        self.save_parameters(num_ayahs=int(num_ayahs),
                             revelation_place=revelation_place,
                             surah_info=surah_info)
    
    def get_ayahs(self):
        futures = []
        ayahs = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(1, self.num_ayahs+1):
                futures.append(executor.submit(self.get_ayah, i))
        for future in concurrent.futures.as_completed(futures):
            ayah_num, arab_ayah, translated_ayah = future.result()
            ayahs.append((ayah_num, arab_ayah, translated_ayah))
        self.save_parameters(ayahs=sorted(ayahs, key=lambda x: x[0]))
    
    def get_ayah(self, i: int):
        url = f"{self.url}/{i}"
        soup = Base.get_soup(url)
        ayah = soup.find("div", attrs={'data-index': "0"})
        arab_ayah = ayah.find("h1").get_text()
        translated_ayah = ayah.select_one("div.TranslationText_text__4atf8").contents[0]
        return i, arab_ayah, translated_ayah

    def get_full_surah(self):
        full_surah = ""
        full_surah_translated = "\n".join([
            ayah for _, ayah, _ in self.ayahs
        ])
        full_surah = "\n".join([
            ayah for _, _, ayah in self.ayahs
        ])
        # for ayah_num, arab_ayah, translated_ayah in self.ayahs:
        #     full_surah_translated += translated_ayah
        self.save_parameters(full_surah=full_surah,
                             full_surah_translated=full_surah_translated)