from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

# 配置 Selenium
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 無頭模式，避免打開瀏覽器窗口
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 初始化 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.12news.com/search?q=intel")

# 點擊“load more results”按鈕，直到沒有更多結果
# while True:
# try:
#     load_more_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'load more results')]"))
#     )
#     load_more_button.click()
#     WebDriverWait(driver, 10).until(
#         EC.staleness_of(load_more_button)
#     )
# except Exception as e:
#     print("No more results to load or error occurred:", e)
        # break

# 抓取所有文章鏈接
links = driver.find_elements(By.XPATH, "//div[contains(@class, 'article')]//h4/a")
print(len(links))
article_urls = [link.get_attribute('href') for link in links]

# 定義保存結果的 CSV 文件
csv_file = open('articles.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['URL', 'Title', 'Author', 'Content'])

# 遍歷所有文章鏈接並抓取詳細信息
for url in article_urls:
    driver.get(url)
    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/h1"))
        ).text
        author = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/aside/div[1]").text
        content_elements = driver.find_elements(By.XPATH, "/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/div[4]//p")
        content = ' '.join([element.text for element in content_elements])
        
        csv_writer.writerow([url, title, author, content])
    except Exception as e:
        print("Error occurred while processing article:", e)
        continue

# 關閉 CSV 文件和 WebDriver
csv_file.close()
driver.quit()
