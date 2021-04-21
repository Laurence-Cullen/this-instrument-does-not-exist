import concurrent.futures
import contextlib
import math
import os
from http import HTTPStatus
from pathlib import Path

import requests
from serpapi import GoogleSearch
from tqdm import tqdm

MAX_WORKERS = 200

instruments = [
    "guitar",
    "piano",
    "hammered dulcimer",
    "drum set",
    "drums",
    "violin",
    "nyckelharpa",
    "hurdy gurdy",
    "harp",
    "qanun",
    "duduk",
    "melodeon",
    "glass armonica",
    "lute",
    "marxophone",
    "tambura",
    "mbira",
    "xylophone",
    "timpani",
    "cittern",
    "pipe organ",
    "saxophone",
    "flute",
    "cornet",
    "trumpet",
    "marimba",
    "theramin",
    "bass guitar",
    "electric keyboard",
    "tuba",
    "harmonica",
    "euphonium",
    "bass recorder",
    "oboe",
    "banjo",
    "viola",
    "cello",
    "erhu",
    "trombone",
    "guzheng",
    "koto",
    "clarinet",
    "cymbal",
    "gong",
    "shamisen"
]

supported_extensions = [
    "jpg",
    "png",
    "jpeg",
    "JPG",
    "JPEG"
]
headers = {
    'User-Agent': 'this-instrument-does-not-exist/0.1 (https://github.com/Laurence-Cullen/this-instrument-does-not-exist; laurencesimoncullen@gmail.com)',
    'From': 'laurencesimoncullen@gmail.com'  # This is another valid field
}


def download_file(url: str):
    response = requests.get(url, headers=headers)

    if response.status_code != HTTPStatus.OK:
        print(f"status code {response.status_code} for url {url}")
        print(f"text: {response.text}")
        return None

    return response.content


def get_image_results_for_query(query: str, num_images: int = 100):
    results = []

    for page_num in tqdm(range(math.ceil(num_images / 100))):
        params = {
            "api_key": os.getenv("SERPAPI_KEY"),
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "tbs": "il:cl",
            "hl": "en",
            "tbm": "isch",
            "ijn": page_num
        }

        # tbs is licence, ijn is page
        search = GoogleSearch(params)
        result = search.get_dict()
        with contextlib.suppress(KeyError):
            results += result['images_results']

    return results


def download_images_for_query(query: str, save_dir: Path, images_per_query: int):
    results = get_image_results_for_query(query, images_per_query)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        jobs = {}
        for i, result in enumerate(results):
            url = result['original']
            jobs[(executor.submit(download_file, url))] = (url, i)
        for future in tqdm(concurrent.futures.as_completed(jobs)):
            try:
                image_data = future.result()
            except Exception as e:
                print(f"exception: {e} for url: {url}")
                continue
            url, i = jobs[future]

            print(f"{i * 100 / len(results)}%")

            extension = url.split(".")[-1]
            if extension not in supported_extensions:
                if "jpg" in extension:
                    extension = "jpg"
                elif "png" in extension:
                    extension = "png"
                else:
                    print(f"extension: {extension}, not supported for url: {url}")
                    continue

            if image_data is not None:
                with open(save_dir / f"{i}.{extension}", mode="wb") as f:
                    f.write(image_data)


def main():
    data_dir = Path("data-large")
    images_per_instrument = 10000

    for instrument in tqdm(["guitar"]):
        save_dir = data_dir / instrument
        # if save_dir.exists():
        #     continue
        save_dir.mkdir(parents=True, exist_ok=True)
        download_images_for_query(instrument, save_dir=save_dir, images_per_query=images_per_instrument)


if __name__ == '__main__':
    main()
