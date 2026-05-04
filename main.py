from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time, sys, argparse
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
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

URL = 'https://www.e-typing.ne.jp'
TYPING_URL = 'https://www.e-typing.ne.jp/../app/standard.asp?sct=trysc.trysc.trysc&st=std&im=0'
TIMEOUT = 10
key_pressed = False


def on_press(key):
    if key == Key.f8:
        return False
    return True

def on_release(key):
    if key == Key.f8:
        return False
    return True

def on_press_key(key):
    global key_pressed
    key_pressed = True

def on_release_key(key):
    global key_pressed
    key_pressed = False

def login(driver, username: str, password: str):
    try:
        driver.get(URL)
        txtLoginId = driver.find_element(by=By.NAME, value='f_em')
        txtPassword = driver.find_element(by=By.NAME, value='f_pw')
        submit_button = driver.find_element(by=By.ID, value='login_btn')
        txtLoginId.send_keys(username)
        txtPassword.send_keys(password)
        submit_button.click()
        WebDriverWait(driver, TIMEOUT).until(
            EC.any_of(
                EC.url_contains("/member/"),
                EC.url_contains("error.asp")
            )
        )
        if "error.asp" in driver.current_url:
            print("Login failed!")
            driver.quit()
            sys.exit(-1)
    except Exception as E:
        print(E)
        driver.quit()
        sys.exit(-1)

def go_to_typing_frame(driver):
    driver.get(TYPING_URL)
    typing = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "start_btn")))
    ActionChains(driver).click(typing).perform()

def auto_typing(driver, keyboard):
    try:
        print("START TYPING")
        keyboard.press(Key.space)
        keyboard.release(Key.space)
        time.sleep(3)
    
        listener = Listener(on_press=on_press_key, on_release=on_release_key)
        listener.start()

        while True:
            span_tag = driver.find_elements(
                By.XPATH,
                "//div[@id='sentenceText']//span"
            )
            if len(span_tag) == 2:
                target = span_tag[1]
            else:
                time.sleep(0.05)
                continue
            print(target.text)
            for character in target.text:
                driver.execute_script("""
                    if (!window.customKeyHandler) {
                        window.customKeyHandler = function(e) {
                            e.preventDefault();
                            e.stopImmediatePropagation();
                            const newEvent = new KeyboardEvent(e.type, {
                                key: e.key,
                                code: e.code,
                                bubbles: true
                            });
                            document.dispatchEvent(newEvent);
                        };
                        ['keydown','keypress','keyup'].forEach(type => {
                            window.addEventListener(type, window.customKeyHandler, true);
                        });
                    }
                """)
                while True:
                    if key_pressed: break
                    time.sleep(0.005)
                driver.execute_script("""
                    if (window.customKeyHandler) {
                        ['keydown','keypress','keyup'].forEach(type => {
                            window.removeEventListener(type, window.customKeyHandler, true);
                        });
                        window.customKeyHandler = null;
                    }
                """)
                keyboard.press(character)
                keyboard.release(character)
            time.sleep(0.5)
    except Exception as E:
        print(E)
        driver.quit()
        sys.exit(-1)

def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <username> <password>" % sys.argv[0])
        print("(+) Example: %s abc@gmail.com your_stupid_password" % sys.argv[0])
        sys.exit(-1)
    username = sys.argv[1]
    password = sys.argv[2]

    driver = webdriver.Chrome(options=chrome_options)
    keyboard = Controller()

    login(driver, username, password)
    go_to_typing_frame(driver)
    # Wait until press f8 to start
    with Listener(on_press=on_press, on_release=on_release) as listener: # type: ignore
        listener.join()
    auto_typing(driver, keyboard)
    # time.sleep(9999)

    driver.quit()

if __name__ == '__main__':

    main()
