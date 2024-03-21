import pyautogui

# منتظر شدن برای مشاهده صفحه دوم (در این مثال ۵ ثانیه انتظار می‌کشیم)
# pyautogui.sleep(5)

# گرفتن اسکرین‌شات
screenshot = pyautogui.screenshot()

# ذخیره‌ی اسکرین‌شات با یک نام فایل
screenshot.save('screenshot.png')
