import os
import sys
import requests
import time
from playwright.sync_api import sync_playwright

def send_tg_msg(message):
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": message})
        except Exception as e:
            print(f"发送Telegram消息失败: {e}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # --- 核心修改：通过 URL 下载脚本并直接注入字符串 ---
        stealth_url = "https://raw.githubusercontent.com/requirecool/playwright-stealth/master/playwright_stealth/stealth.min.js"
        try:
            stealth_js = requests.get(stealth_url).text
            page.add_init_script(script=stealth_js)
        except Exception as e:
            print(f"注入 Stealth 脚本失败，继续执行: {e}")

     

        try:
            print("正在访问网站...")
            page.goto("https://pixelforge.gg/dashboard", wait_until="networkidle")
            
            # --- [调试逻辑] 打印所有 input 的信息 ---
            inputs = page.query_selector_all("input")
            print(f"DEBUG: 页面共发现 {len(inputs)} 个输入框")
            for i, inp in enumerate(inputs):
                tag_id = inp.get_attribute('id')
                tag_name = inp.get_attribute('name')
                tag_type = inp.get_attribute('type')
                tag_placeholder = inp.get_attribute('placeholder')
                print(f"输入框 {i}: id='{tag_id}', name='{tag_name}', type='{tag_type}', placeholder='{tag_placeholder}'")
            # ------------------------------------

            print("调试信息已打印，程序即将结束。")
            
        except Exception as e:
            error_msg = f"❌ 续期失败: {str(e)}"
            print(error_msg)
            send_tg_msg(error_msg)
        finally:
            browser.close()



if __name__ == "__main__":
    run()
