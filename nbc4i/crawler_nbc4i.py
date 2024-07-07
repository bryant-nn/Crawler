import requests
from bs4 import BeautifulSoup
import csv
import time
import regex
from datetime import datetime

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def get_news_data(keyword):
    base_url = "https://www.nbc4i.com"
    news_data = []
    page = 1

    while True:
        if page == 1:
            url = f"{base_url}/?submit=&s={keyword}"
        else:
            url = f"{base_url}/page/{page}/?submit&s={keyword}"

        print(f"Fetching: {url}")
        response = requests.get(url, headers={'User-Agent': user_agent})
        print(response)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('h2', class_='article-list__article-title')

        if not articles:
            print("No more articles found. Stopping.")
            break

        for article in articles:
            link = article.find('a')['href']
            article_data = get_article_content(link)
            if article_data:
                news_data.append(article_data)

        print(f"Processed page {page}")
        page += 1
        time.sleep(5)  # Be polite to the server

    return news_data

def get_article_content(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch article content for {url}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('h1', class_='article-header__title')
        title = title.text.strip() if title else "No title found"
        
        # Extract publication date
        date = soup.find('time', class_='article-date')
        publ_dt = date['datetime'] if date and 'datetime' in date.attrs else ""
        
        # Extract content
        content_div = soup.find('div', class_='rich-text')
        if content_div:
            paragraphs = content_div.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = "\n\n".join([process_content(p.get_text(strip=True)) for p in paragraphs if p.get_text(strip=True)])
        else:
            print(f"Could not find content for {url}")
            content = ""
        
        return {
            'src_url': url,
            'publ_dt': publ_dt,
            'title': title,
            'content': content
        }
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
    
    return None

def process_content(content):
    # 處理單個段落內的空白
    _REGEXP_MULTI_SPACE = regex.compile(r"(?<space>\s)+")
    content = _REGEXP_MULTI_SPACE.sub(" ", content)
    return content.strip()

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['src_url', 'publ_dt', 'title', 'content'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    keyword = "tsmc"
    news_data = get_news_data(keyword)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{keyword}_news_data_{timestamp}.csv"
    save_to_csv(news_data, filename)
    print(f"Saved {len(news_data)} articles to {filename}")