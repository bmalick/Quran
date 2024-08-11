import sys; sys.path.append('.')

from argparse import ArgumentParser
from tqdm import tqdm
import concurrent.futures

# todo: quran command
from src.surah import Surah

def main():
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in tqdm(range(1,115), desc="Surah crawling"):
            surah = Surah(i)
            futures.append(executor.submit(surah.create))
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ =="__main__":
    main()
