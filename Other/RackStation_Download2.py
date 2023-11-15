#WIP

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import requests
import hashlib
import time
import sys

class Main:
    def __init__(self):
        self.PASS = 'PASSWORD_HERE'
        self.URLS = [('FIRST_URL_HERE','FIRST_MD5_HERE'),
                     ('SECOND_URL_HERE','SECOND_MD5_HERE')]
        
    def download_file(self,download_url,sharing_sid,filename):
        print("Downloading File: " + filename)
        headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language' : 'en-US,en;q=0.5',
                    'Accept-Encoding' : 'gzip, deflate, br',
                    'DNT' : '1', 
                    'Connection' : 'keep-alive',
                    'Referer' : download_url,
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

    def checkhash(self, filename, given_hash):
        hash = hashlib.md5()
        with open(filename, 'rb') as f:
            while chunk := f.read(8192):
                hash.update(chunk)
        hash = hash.hexdigest()
        if hash == given_hash:
            print(f"{filename}: MD5 Checksum passed!")
            return True
        else:
            print(f"{filename}: MD5 Checksum failed!")
            return False
    
    def process_file(self, url, password, hash):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless=new')
        driver = webdriver.Chrome(options=opt)
        driver.delete_all_cookies()
        driver.get(url)
        print("Waiting for URL to Load...")
        WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                        (By.XPATH, '//div[contains(@class, "x-panel-bwrap")]')
                ))
        print("Loaded!")
        text_box = driver.find_element(by=By.NAME, value="passwd")
        submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
        text_box.send_keys(password)
        print("Attempting Password")
        submit_button.click()
        time.sleep(1)
        error_box = driver.find_element(by=By.ID, value="webfm-login-dialog-status")
        error_text = error_box.get_attribute("textContent")
        if error_text != "":
            print(error_text)
            sys.exit(1)
        else:
            print("Correct Password!")
        print("Waiting for Cookie...")
        sharing_sid = WebDriverWait(driver, 120).until(lambda d: d.get_cookie('sharing_sid'))['value']
        print("Cookie Got!")
        filename = driver.find_element(By.XPATH,'//div[contains(@class, "webfm-download-filename")]').get_attribute("textContent")
        if "/sharing/" in url:
            download_url = url.replace("/sharing/", "/fsdownload/") + "/" + filename
        elif "/fbsharing/" in url:
            download_url = url.replace("/fbsharing/", "/fsdownload/fbsharing-") + "/" + filename
        else:
            print("Unkown url format!")
            exit(1)
        self.download_file(download_url,sharing_sid,filename)
        driver.close()
        try:
            if not self.checkhash(filename,hash):
                sys.exit(1)
        except:
            print(f"Hash not found!")

    def runapp(self):
        current = 0
        total = len(self.URLS)
        for pair in self.URLS:
            current += 1
            print(f"Downloading file {current}/{total}: {pair[0]}") 
            try:
                curURL = pair[0]
                curHash = pair[1]
                self.process_file(curURL, self.PASS, curHash)
            except Exception as e:
                print(f"Download Failed!\nError: {e}")
                sys.exit(1)
        sys.exit(0)

if __name__ == '__main__':
    runtime = Main()
    runtime.runapp()
