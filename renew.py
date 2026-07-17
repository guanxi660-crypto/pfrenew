import os
import sys
import requests
# 确保 playwright 模块可用
try:
    from playwright.sync_api import sync_playwright
    from playwright_stealth import stealth_sync
except ImportError as e:
    print(f"依赖库未安装: {e}")
    sys.exit(1)

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
        # 显式使用 chromium
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        # 应用反检测
        stealth_sync(page)

        try:
            print("正在访问网站...")
            page.goto("https://pixelforge.gg/dashboard", wait_until="networkidle")
            
            # 填入登录信息
            page.fill('input[name="email"]', os.getenv("PF_USERNAME", ""))
            page.fill('input[name="password"]', os.getenv("PF_PASSWORD", ""))
            page.click('button[type="submit"]')
            
            # 等待操作完成
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
            send_tg_msg(error_msg)
        finally:
            browser.close()

if __name__ == "__main__":
    run()
