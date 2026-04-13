import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def scrape_engage_jobs_auto():
    # 1. GitHub Secrets から設定を読み込む
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.getenv('USER_ID')

    # 2. Chromeのオプション設定（クラウド実行用）
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 画面を表示しない
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 3. ブラウザの起動
    driver = webdriver.Chrome(options=chrome_options)

    # 4. 求人検索（テスト用に沖縄の「求人」全体で検索）
    # area=47 は沖縄県です。keywordを「求人」にしてヒット率を上げています。
    search_url = "https://en-gage.net/user/search/list/?keyword=求人&area=47"
    driver.get(search_url)
    time.sleep(3)  # 読み込み待ち

    # 5. 求人情報の抽出
    job_elements = driver.find_elements(By.CSS_SELECTOR, "div.p-search_list_item")
    
    new_jobs = []
    for job in job_elements[:3]:  # 最新3件を取得
        try:
            title = job.find_element(By.CSS_SELECTOR, "h3").text
            link = job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            new_jobs.append(f"【新着】{title}\n{link}")
        except:
            continue

    driver.quit()

    # 6. LINE送信処理
    if new_jobs:
        message = "\n\n".join(new_jobs)
        send_line_message(line_token, user_id, message)
        print(f"{len(new_jobs)}件の求人を送信しました。")
    else:
        print("新しい求人は見つかりませんでした。")

def send_line_message(token, to_user, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": to_user,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    
    # LINE側のエラーをログに出す（重要！）
    if response.status_code != 200:
        print(f"LINE送信エラー: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    scrape_engage_jobs_auto()
