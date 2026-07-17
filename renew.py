import os
import requests
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

        # 注入 Stealth 脚本以防检测
        try:
            stealth_js = requests.get("https://raw.githubusercontent.com/requirecool/playwright-stealth/master/playwright_stealth/stealth.min.js").text
            page.add_init_script(script=stealth_js)
        except Exception as e:
            print(f"注入 Stealth 脚本失败: {e}")

        try:
            print("正在访问网站...")
            page.goto("https://pixelforge.gg/dashboard", wait_until="networkidle")
            
            # --- 使用 ID 选择器进行操作 ---
            print("正在输入账号信息...")
            page.fill('#email', os.getenv("PF_USERNAME", ""))
            page.fill('#password', os.getenv("PF_PASSWORD", ""))
            
            # 点击登录按钮 (这里假设按钮类型是 submit，如果点击没反应，可尝试使用 text="Login" 或类似选择器)
            print("正在提交登录...")
            page.click('button[type="submit"]')
            
            # 等待登录后的页面加载
            page.wait_for_load_state("networkidle")
            
            # 点击 Renew 按钮
            print("正在尝试点击 Renew...")
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
