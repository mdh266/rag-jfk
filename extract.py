import requests
from bs4 import BeautifulSoup
import asyncio
import json
from typing import Dict, Union, Tuple
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.exceptions import Conflict
import re
##################################################################
# python extract.py  38.57s user 1.47s system 6% cpu 9:37.97 total
##################################################################


async def get_soup(address: str, num: int = None) -> str:
    if num is not None:
        page = requests.get(f"{address}?page={num}")
    else:
        page = requests.get(f"{address}")
        
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


async def get_links():
    address = "https://www.jfklibrary.org/archives/other-resources/john-f-kennedy-speeches"
    page_nbs = range(1,33)

    links = []
    for num in page_nbs:
        soup = await get_soup(address, num)
        links.extend([article.find("a")["href"] for article in soup.find_all("article")])
            
    return links


def get_name(link: str) -> str:
    name = link.partition("/john-f-kennedy-speeches/")[2]
    return f"{name}"


def strip_title(text: str) -> str:
    # Remove '| JFK Library' if it exists in the string
    if " | JFK Library" in text:
        text = text.replace(" | JFK Library", "").strip()

    return text


def find_sources(text: str) -> Union[str, Tuple[str, str]]:
    # Regular expression to match 'Source:' or 'Sources:' (case-sensitive)
    match = re.search(r'(Source:|Sources:)', text)
    
    if match:
        # Find the position of the match
        match_pos = match.start()

        # Split the text into two parts
        before_text = text[:match_pos].strip()  # Text before the match
        after_text = text[match.end():].strip()  # Text after the match

        return [before_text, after_text]
    else:
        return text  # Return None if neither 'Source:' nor 'Sources:' is found


async def get_document(link: str) -> None:
    address = f"https://www.jfklibrary.org/{link}"
    filename = get_name(link)
    soup = await get_soup(address)

    title = strip_title(soup.find('title').text)
    result = find_sources(soup.find("article").text)
    source = ""

    if isinstance(result, list):
        text, source = result
    else:
        text = result

    doc = {
           "title": title,
           "text": text,
           "filename": filename,
           "source": source,
           "url": address
    }

    return doc


async def save_document(bucket, doc: Dict[str, str]) -> None:
    file_name = doc.get("filename")
    blob = bucket.blob(f"{file_name}.json")
    blob.upload_from_string(data=json.dumps(doc))
    

async def load(bucket, link: str) -> None:
    doc = await get_document(link)
    await save_document(bucket, doc)


async def main():
    credentials = (service_account.Credentials
                                  .from_service_account_file('credentials.json'))

    client = storage.Client(project=credentials.project_id,
                            credentials=credentials)

    links = await get_links()
    
    try:
        bucket = client.create_bucket("kennedyskis")
    except Conflict:
        bucket = client.get_bucket("kennedyskis")

    files = []
    for link in links:
        try: 
            await load(bucket, link)
            files.append(get_name(link))
        except Exception as e:
            with open("uploaded_files.json", "w") as f:
                f.write(json.dumps({"uploaded": files,
                                    "exception": e}))
                
    with open("uploaded_files.json", "w") as f:
        f.write(json.dumps({"uploaded": files}))

if __name__ == "__main__":
    asyncio.run(main())
