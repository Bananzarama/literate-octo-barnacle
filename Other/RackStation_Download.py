# For downloading large files from a rackstation server outside of a browser.
# Still uses chrome for setup.
# Just set url and password then download away.
# Made by Ryan w/ help from Vinay.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import requests

class Main:
    def __init__(self):
        self.URL = ''
        self.PASS = ''

    def download_file(self,download_url,sharing_sid,filename):
        print("Downloading File: " + filename)
        headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language' : 'en-US,en;q=0.5',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'DNT' : '1', 
                    'Connection' : 'keep-alive',
                    'Referer' : self.URL,
                    'Cookie' : 'sharing_sid={}'.format(sharing_sid),
                    'Upgrade-Insecure-Requests' : '1',
                    'Sec-Fetch-Dest' : 'document',
                    'Sec-Fetch-Mode' : 'navigate',
                    'Sec-Fetch-Site' : 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Pragma' : 'no-cache',
                    'Cache-Control' : 'no-cache',
                    'TE' : 'trailers'}
        with requests.get(download_url, headers=headers, stream=True) as r:
            total_size_in_bytes= int(r.headers.get('content-length', 0))
            block_size = 1024 
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for data in r.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
        print("File Downloaded!")
        return filename

    def runapp(self):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless=new')
        driver = webdriver.Chrome(options=opt)
        driver.delete_all_cookies()
        driver.get(self.URL)
        print("Waiting for URL to Load...")
        WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                        (By.XPATH, '//div[contains(@class, "x-panel-bwrap")]')
                ))
        print("Loaded!")
        text_box = driver.find_element(by=By.NAME, value="passwd")
        submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
        text_box.send_keys(self.PASS)
        submit_button.click()
        print("Waiting for Cookie...")
        sharing_sid = WebDriverWait(driver, 120).until(lambda d: d.get_cookie('sharing_sid'))['value']
        print("Cookie Got!")
        filename = driver.find_element(By.XPATH,'//div[contains(@class, "webfm-download-filename")]').get_attribute("textContent")
        download_url = self.URL.replace("/sharing/", "/fsdownload/") + "/" + filename
        self.download_file(download_url,sharing_sid,filename)
        driver.close()
        quit()

if __name__ == '__main__':
    runtime = Main()
    runtime.runapp()
