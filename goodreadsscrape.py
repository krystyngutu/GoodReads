import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# GoodReads list URL
url = "https://www.goodreads.com/review/list/68426939"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

# Request page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

books = []

bookRows = soup.select("tr")

for row in bookRows:
    try:
        title = row.select_one(".title a").text.strip()
        author = row.select_one(".author a").text.strip()

        # Clean up average rating - remove "avg rating" prefix
        avgRating = row.select_one(".avg_rating")
        avgRating = avgRating.text.replace("avg rating", "").strip() if avgRating else "N/A"

        # Extract actual date added
        dateAdded = row.select_one(".date_added span")
        dateAdded = dateAdded.text.strip() if dateAdded else "N/A"

        # Clean up date published - remove "date pub" prefix
        datePublished = row.select_one(".date_pub")
        datePublished = datePublished.text.replace("date pub", "").strip() if datePublished else "N/A"

        # Clean up pages - remove everything after the number
        pages = row.select_one(".num_pages")
        if pages:
            pages = pages.text.split()[0]
        else:
            pages = "N/A"
        bookLink = "https://www.goodreads.com" + row.select_one(".title a")["href"]

        books.append({
            "Title": title,
            "Author": author,
            "Average Rating": avgRating,
            "Date Added": dateAdded,
            "Date Published": datePublished,
            "Pages": pages,
            "Book Link": bookLink,
        })

    except AttributeError:
        continue

# Save extracted data to CSV file
df = pd.DataFrame(books)
df.to_csv("goodreads_books_page1.csv", index=False)

print(f"Scraped {len(books)} books from the first page and saved them to 'goodreads_books_page1.csv'.")

# Function to scrape book details
def scrapeBookDetails(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract summary (under "TruncatedContent")
    summaryElement = soup.select_one(".TruncatedContent")
    summaryText = summaryElement.text.strip() if summaryElement else "N/A"

    # Extract number of pages
    pagesElement = soup.select_one(".BookDetails")
    pagesText = pagesElement.text.strip() if pagesElement else "N/A"

    # Extract genres (from "genresList")
    genresContainer = soup.select_one(".BookPageMetadataSection__genres")

    if genresContainer:
        genres = [genre.text.strip() for genre in genresContainer.find_all("a")]
        genresText = ", ".join(set(genres)) if genres else "N/A"
    else:
        genresText = "N/A"

    return summaryText, pagesText, genresText

# Iterate through each book link
for index, row in df.iterrows():
    try:
        summary, pages, genres = scrapeBookDetails(row["Book Link"])
        df.at[index, "Summary"] = summary
        df.at[index, "Pages"] = pages
        df.at[index, "Genres"] = genres

        print(f"Processed: {row['Title']} ✅")

        # Add delay to avoid being blocked
        time.sleep(2)
    except Exception as e:
        print(f"Error processing {row['Book Link']}: {e}")
        continue

    # Save updated data
    df.to_csv("goodreads_books.csv", index = False)

print("Scraping completed. Data saved to 'goodreads_books.csv'.")
