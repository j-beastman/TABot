import os
import typing as T
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

pdf_directory = "deeplake/data/pdf"
txt_directory = "deeplake/data/txt"

def get_cs40_docs() -> T.Dict:
    source_dictionary = {}
    # URL of the webpage
    url = "https://www.cs.tufts.edu/comp/40/resources/resources.html"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the anchor tags (links)
    links = soup.find_all("a")

    # Loop through the links
    for link in links:
        href = link.get("href")
        if href:
            # Build the absolute URL by combining the base URL and the relative link
            absolute_url = urljoin(url, href)
            # Send a GET request to the link
            try:
                link_response = requests.get(absolute_url)
            except requests.exceptions.RequestException as e:
                print("Encountered error ", e, " from ", absolute_url)
                with open("texts_to_get.txt", "a", encoding='utf-8') as txt_file:
                    txt_file.write(absolute_url)
                    txt_file.write("\n")
            if absolute_url == "https://hikage.freeshell.org/books/theCprogrammingLanguage.pdf":
                continue
            if href.endswith(".pdf"):
                # Generate the full path to the file
                filename = os.path.join(pdf_directory, href.split("/")[-1])

                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # Write the PDF content to the file
                with open(filename, "wb") as pdf_file:
                    pdf_file.write(link_response.content)

                source_dictionary[filename] = href
                
            elif href.endswith(".html"):
                # Parse the content of the linked page
                link_soup = BeautifulSoup(link_response.content, "html.parser")

                # Extract the content of the linked page
                content = link_soup.get_text()

                # Generate the full path to the file
                filename = os.path.join(txt_directory, href.split("/")[-1])
                filename = filename.replace(".html", ".txt")

                source_dictionary[filename] = absolute_url

                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)

                # Write the content to the file
                with open(filename, "w", encoding='utf-8') as txt_file:
                    txt_file.write(content)
            else:
                with open("texts_to_get.txt", "a", encoding='utf-8') as txt_file:
                    txt_file.write(absolute_url)
                    txt_file.write("\n")
    return source_dictionary

