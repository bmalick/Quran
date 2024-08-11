import sys; sys.path.append('.')

from argparse import ArgumentParser
from tqdm import tqdm
import concurrent.futures

# todo: quran command
from src.surah import Surah

def main(args):
    surah = Surah(args.num).create()

if __name__ =="__main__":
    parser = ArgumentParser()
    parser.add_argument("--num", "-n", required=True, type=int)
    args = parser.parse_args()
    main(args)
