from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
import json, os, time, shutil, random, sys, argparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pynput.keyboard import Key, Controller, Listener

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument('--start-maximized')

# disable announcement
# prefs = {
#     "credentials_enable_service": False,
#     "profile.password_manager_enabled": False,
#     "profile.password_manager_leak_detection": False
# }
# chrome_options.add_experimental_option("prefs", prefs)
# Disable annountcement
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

URL = 'https://www.e-typing.ne.jp/roma/check/'
TYPING_URL = 'https://www.e-typing.ne.jp/app/jsa_std/typing.asp?t=trysc.trysc.trysc.std.0&u=&s=0'
TIMEOUT = 5

def on_press(key):
    if key == Key.f8:
        return False
    return True

def on_release(key):
    if key == Key.f8:
        return False
    return True

def go_to_typing_frame(driver):
    driver.get(TYPING_URL)
    typing = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "start_btn")))
    ActionChains(driver).click(typing).perform()
    time.sleep(1)

def auto_typing(driver, keyboard, mn=0.05, mx=0.2):
    try:
        print("START TYPING")
        keyboard.press(Key.space)
        keyboard.release(Key.space)
        time.sleep(4)
    
        while True:
            span_tag = driver.find_elements(
                By.XPATH,
                "//div[@id='sentenceText']//span"
            )
            if len(span_tag) != 2: break
            else: target = span_tag[1]
            print(target.text)
            for character in target.text:
                keyboard.press(character)
                keyboard.release(character)
                delay = random.uniform(mn, mx)
                print(delay)
                time.sleep(delay)
            time.sleep(0.4)
    except Exception as E:
        print(E)
        sys.exit(-1)

def main(mn, mx):
    driver = webdriver.Chrome(options=chrome_options)
    keyboard = Controller()

    go_to_typing_frame(driver)
    # Wait until press f8 to start
    with Listener(on_press=on_press, on_release=on_release) as listener: # type: ignore
        listener.join()
    auto_typing(driver, keyboard, mn, mx)
    time.sleep(60)

    driver.quit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Auto typing tools')
    parser.add_argument('--min-delay', type=float,
                        help='Min time delay between press key')
    parser.add_argument('--max-delay', type=float,
                        help='Max time delay between press key')
    args = parser.parse_args()

    mn, mx = 0.1, 0.2 # Default
    if args.min_delay: mn = args.min_delay
    if args.max_delay: mx = args.max_delay

    main(mn, mx)
