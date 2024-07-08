import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

# 配置 Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # 無頭模式，避免打開瀏覽器窗口
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# 初始化 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 隱藏 Selenium 特徵
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    '''
})

keywords = ['intel', 'intel fab', 'intel foundry', 'samsung', 'samsung fab', 'samsung foundry', 'globalfoundries', 'globalfoundries fab', 'smic', 'smic fab', 'united microelectronics', 'united microelectronics fab']

# 用於保存結果的 DataFrame
articles_data = []

for keyword in keywords:
    url = f'https://www.nbc4i.com/?submit=&s={keyword}+&orderby=modified'
    driver.get(url)


    # 抓取所有文章鏈接
    # /html/body/div[1]/div/div[2]/div[2]/div/main/section/div/article[13]/div/h2/a
    articles = driver.find_elements(By.XPATH, "//div[contains(@class, 'article-list__article-text')]//h2/a")
    article_urls = [article.get_attribute('href') for article in articles]
    print(f'Found {len(article_urls)} articles for keyword: {keyword}')
    quit()

    # 遍歷所有文章鏈接並抓取詳細信息
    for url in tqdm(article_urls):
        driver.get(url)
        try:
            title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/h1"))
            ).text
            author = driver.find_element(By.XPATH, "//html/body/div[2]/div/div[2]/div[1]/header/div/div/div[2]/p[1]/a").text
            time_ = driver.find_element(By.XPATH, "//html/body/div[2]/div/div[2]/div[1]/header/div/div/div[2]/p[2]/time").text
            paragraphs = driver.find_elements(By.XPATH, "//div[@class='article-content article-body rich-text ']//p")
            content = ' '.join([paragraph.text for paragraph in paragraphs])
            
            articles_data.append({
                'URL': url,
                'Title': title,
                'Author': author,
                'Time': time_,
                'Content': content
            })
        except Exception as e:
            print("Error occurred while processing article:", e)
            continue

# 關閉 WebDriver
driver.quit()

# 使用 Pandas 保存結果到 CSV 文件
df = pd.DataFrame(articles_data)
df.to_csv('articles.csv', index=False, encoding='utf-8')
