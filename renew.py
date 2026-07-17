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
            
            # 填入信息 (如果报错找不到元素，请确保网站确实加载了这些 input)
            page.fill('input[name="email"]', os.getenv("PF_USERNAME", ""))
            page.fill('input[name="password"]', os.getenv("PF_PASSWORD", ""))
            page.click('button[type="submit"]')
            
            page.wait_for_load_state("networkidle")
            
            # 尝试点击 Renew
            renew_selector = 'button:has-text("Renew")'
            page.wait_for_selector(renew_selector, timeout=15000)
            page.click(renew_selector)
            
            send_tg_msg("✅ PixelForge 续期成功！")
            print("续期成功")
        except Exception as e:
            error_msg = f"❌ 续期失败: {str(e)}"
            print(error_msg)
            # 在 GitHub Actions 日志中打印页面内容，方便排查定位
            print(page.content()[:500]) 
            send_tg_msg(error_msg)
        finally:
            browser.close()


if __name__ == "__main__":
    run()
