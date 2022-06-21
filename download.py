import requests
import os
from pyquery import PyQuery as PQ



def get_alllinks(url):
    pq = PQ(requests.get(url).content)
    links = pq(".paragraphs-item-content-text .content a")
    urls = []
    for link in links:
        urls.append(PQ(link).attr("href"))
    return urls

def download_files(url, folder):
    try:
        os.makedirs(folder)
    except:
        pass
    pq = PQ(requests.get(url).content)
    links = pq(".content table td a")
    for link in links:
        pq = PQ(link)
        name = pq.text()
        url = pq.attr("href")
        if url is None or name is None:
            continue
        resp = requests.get(url, stream=True)
        print(f"downloading {name} from {url}")
        with open(os.path.join(folder, name), "wb+") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)


if __name__ == "__main__":
    download_files("https://engineering.case.edu/bearingdatacenter/normal-baseline-data", "data/cwru_data/normal")
    download_files("https://engineering.case.edu/bearingdatacenter/12k-drive-end-bearing-fault-data", "data/cwru_data/12KDriveEnd")
    download_files("https://engineering.case.edu/bearingdatacenter/48k-drive-end-bearing-fault-data", "data/cwru_data/48KDriveEnd")
    download_files("https://engineering.case.edu/bearingdatacenter/12k-fan-end-bearing-fault-data", "data/crwu_data/FanEnd")
