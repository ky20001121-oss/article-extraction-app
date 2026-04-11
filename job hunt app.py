import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def scrape_engage_jobs_auto():
    profile_path = os.path.join(os.path.expanduser("~"), "Desktop", "engage_profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("detach", True)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        wait = WebDriverWait(driver, 15)
        print("エンゲージへアクセス中...")
        driver.get("https://en-gage.net/")

        print("\n--- 確認 ---")
        input("ログイン済みならそのままEnter。広告等があれば消してからEnter...")

        # --- 検索処理 ---
        print("検索窓を操作しています...")
        # 検索窓のセレクタを複数候補で探す
        search_selectors = ["input[placeholder*='キーワード']", "input[type='text']", ".searchInput"]
        search_input = None
        
        for sel in search_selectors:
            try:
                search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                if search_input: break
            except: continue

        if not search_input:
            print("検索窓が見つかりませんでした。手動で検索して結果を出してからEnterを押してください。")
            input("結果画面が出たらEnter...")
        else:
            search_input.click()
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.DELETE)
            search_input.send_keys("Java 那覇 未経験")
            search_input.send_keys(Keys.ENTER)
            print("検索実行。読み込み中...")
            time.sleep(7) # 画面遷移を長めに待つ

        # --- 抽出処理 ---
        print("求人情報をスキャン中...")
        
        # 画面内のすべてのaタグから求人情報をぶっこ抜くJS
        js_code = """
        let result = [];
        let links = document.querySelectorAll('a');
        for (let link of links) {
            let href = link.href;
            let text = link.innerText.trim();
            // URLに 'desc' や 'work' や 'detail' が含まれるものを抽出
            if (href.includes('/desc/') || href.includes('work_id=') || href.includes('/detail/')) {
                if (text.length > 5) {
                    result.push({href: href, text: text});
                }
            }
        }
        return result;
        """
        candidates_data = driver.execute_script(js_code)

        if not candidates_data:
            print("求人データが拾えませんでした。ページがまだ読み込まれていないか、URLが違います。")
            return []

        # --- フィルタリング ---
        ng_keywords = ["事務", "コールセンター", "販売", "接客", "飲食店", "介護", "清掃", "すき家", "ショップ", "受付", "軽作業"]
        must_keywords = ["エンジニア", "開発", "システム", "プログラミング", "Java", "実装", "IT"]

        jobs_dict = {}
        for c in candidates_data:
            title = c['text'].replace('\n', ' ')
            detail_url = c['href']
            
            if detail_url in jobs_dict or "応募へ進む" in title:
                continue
            if any(ng_word in title for ng_word in ng_keywords):
                continue
            if not any(must_word in title for must_word in must_keywords):
                continue

            score = 0
            if 'Java' in title: score += 10
            if '那覇' in title or '沖縄' in title: score += 15
            
            jobs_dict[detail_url] = {"title": title, "detail_url": detail_url, "score": score}

        results = sorted(list(jobs_dict.values()), key=lambda x: x['score'], reverse=True)

        # CSV保存
        csv_file = 'job_results_auto.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'detail_url', 'score'])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n--- 成功！ {len(results)}件抽出しました ---")
        for i, job in enumerate(results[:5], start=1):
            print(f"[{i}] {job['title']}")

        return results

    except Exception as e:
        print(f"エラー発生: {e}")
        return []

if __name__ == "__main__":
    scrape_engage_jobs_auto()