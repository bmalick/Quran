import sys; sys.path.append('.')

from tqdm import tqdm
import concurrent.futures

from src.notion import Notion

def main():

    futures = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in tqdm(range(1,115), desc="Surah crawling"):
            futures.append(executor.submit(Notion().create_surah, Surah(i)))
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ =="__main__": main()