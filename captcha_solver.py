import os
import requests
import whisper
import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time


EDGE_DRIVER_PATH = "D:\Bellek\Investment\FinancialNewsBot\PythonProject\msedgedriver.exe"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61'
SAMPLE_URL = "https://www.google.com/recaptcha/api2/demo"

# TODO : Add "Try Again Later Error" Handling
# TODO : Prepare more applicable user agent and driver path.

class BrowserSetup:

    def __init__(self, driver_path, user_agent):
        self.driver_path = driver_path
        self.user_agent = user_agent

    def __call__(self):
        return self.setup_browser()

    def setup_browser(self):
        try:
            edge_service = Service(self.driver_path)
            edge_options = Options()
            edge_options.add_argument(f'user-agent={self.user_agent}')
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            edge_options.add_argument('--disable-infobars')
            edge_options.add_argument('--disable-extensions')
            edge_options.add_argument('--log-level=3')
            edge_options.add_argument('--silent')
            return webdriver.Edge(service=edge_service, options=edge_options)
        except Exception as e:
            print("Error setting up browser:", {e})


class PageNavigator:

    def __init__(self, browser, url):
        self.browser = browser
        self.url = url
    
    def __call__(self):
        self.navigate_to_page()

    def navigate_to_page(self):
        try:
            self.browser.get(self.url)
        except Exception as e:
            print(f"Error navigating to {self.url}:", {e})


class CaptchaSolver:

    def __init__(self, browser, url):
        self.browser = browser
        self.url = url
    
    def __call__(self):
        self.execute_all()

    def tick_checkbox(self):
        try:
            self.browser.switch_to.default_content()
            self.browser.switch_to.frame(self.browser.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            checkbox_element = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.ID, 'recaptcha-anchor-label')))
            checkbox_element.click()
        except Exception as e:
            print("Error ticking reCaptcha checkbox:", {e})

    def request_audio_version(self):
        try:
            self.browser.switch_to.default_content()
            self.browser.switch_to.frame(self.browser.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']"))
            audio_element = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button')))
            audio_element.click()
        except Exception as e:
            print("Error requesting audio version of reCaptcha:", {e})

    def transcribe(self, audio_url):
        try:
            with open('.temp', 'wb') as f:
                f.write(requests.get(audio_url).content)
            model = whisper.load_model('base')
            result = model.transcribe('.temp', fp16=False)
            return result["text"].strip()
        except Exception as e:
            print("Error while transcribing audio:", {e})

    def send_transcription(self):
        try:
            text = self.transcribe(self.browser.find_element(By.ID, "audio-source").get_attribute('src'))
            self.browser.find_element(By.ID, "audio-response").send_keys(text)
            time.sleep(2)
            self.browser.find_element(By.ID, "recaptcha-verify-button").click()
        except Exception as e:
            print("Error sending transcription:", {e})

    def solve_audio_recaptcha(self):
        try:
            self.tick_checkbox()
            time.sleep(1)
            self.request_audio_version()
            time.sleep(1)
            self.send_transcription()
        except Exception as e:
            print("Error solving audio reCaptcha:", {e})

    def cleanup_temp_files(self):
        try:
            os.remove('.temp')
        except Exception as e:
            print("Error cleaning up temporary files:", {e})

    def execute_all(self):
        self.solve_audio_recaptcha()
        self.cleanup_temp_files()


if __name__ == "__main__":

    browser_instance = BrowserSetup(EDGE_DRIVER_PATH, USER_AGENT)
    browser = browser_instance()
    nav = PageNavigator(browser, SAMPLE_URL)
    nav()
    time.sleep(1)
    solve = CaptchaSolver(browser, SAMPLE_URL)
    solve()
    time.sleep(1)
    browser.quit()



