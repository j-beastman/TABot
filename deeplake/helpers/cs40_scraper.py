import requests
from bs4 import BeautifulSoup

# URL of the webpage
url = "https://www.cs.tufts.edu/comp/40/resources/resources.html"

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all the anchor tags (links)
links = soup.find_all("a")

# Extract and print the href attribute from each anchor tag
for link in links:
    href = link.get("href")
    if href:
        print(href)
