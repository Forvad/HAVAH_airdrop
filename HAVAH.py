import requests
from unicaps import CaptchaSolver, CaptchaSolvingService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import zipfile
import os
from time import sleep
from pyuseragents import random as random_useragent
import tkinter as tk
from selenium.webdriver.common.by import By
from Logs import SaveAddres as Sv
from imap_tools import MailBox, AND
import imaplib
import email
from eth_account import Account
from requests.exceptions import ProxyError
from unicaps.exceptions import BadInputDataError
from selenium.common.exceptions import ElementClickInterceptedException


class HAVANFarm:
    def __init__(self, captcha_name, api_key, reff_url):
        self.driver = None
        self.captcha_name = captcha_name
        self.API_key = api_key
        self.reff_url = reff_url

    @staticmethod
    def address_eth():
        Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = Account.create_with_mnemonic()
        return acct.address

    @staticmethod
    def post(mail, password, name_captha, api_key, proxy_):
        token = HAVANFarm.captcha2(name_captha, api_key)
        cookies = {
            '_ga_3388TR9G64': 'GS1.1.1672247524.1.0.1672247524.0.0.0',
            '_gid': 'GA1.2.805331395.1672247525',
            '_ga_P0J6H1ZDS0': 'GS1.1.1672247604.1.0.1672247604.0.0.0',
            '_ga': 'GA1.1.2051900724.1672247524',
            'CookieConsent': '{stamp:%27o8NH5j6a2jR9MP15f2+qt8a7CqXGaSMZyEk+n8cdyAsg40yaZTZ4Hg==%27%2Cnecessary:'
                             'true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:'
                             '1%2Cutc:1672247602845%2Cregion:%27ru%27}',
            '__Host-next-auth.csrf-token': '45f80066d5c30b5d5e47868638437067887fc54017537bb59d5ee90c4a2b1a81%7C0fcfa'
                                           'a66a7a8d6c07dcea8907823ac19c962a5677039a30101e7b988dbcb2d95',
            '__Secure-next-auth.callback-url': 'https%3A%2F%2Fhavah.io',
        }

        headers = {
            'authority': 'havah.io',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://havah.io',
            'referer': 'https://havah.io/?PageName=signup',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': random_useragent(),
        }

        json_data = {
            'dataSubmit': {
                'email': mail,
                'name': mail.split('@')[0],
                'nickName': mail.split('@')[0],
                'password': 'Qwerty@1234',
                'marketingConsent': True,
                'referralNickName': '',
            },
            'token': token
        }
        proxy_ = {'http': f'http://{proxy_}',
                  'https': f'http://{proxy_}'}
        for _ in range(5):
            try:
                response = requests.post('https://havah.io/api/member', cookies=cookies, headers=headers, json=json_data,
                                         proxies=proxy_)
                print(response.status_code, response.text)
                sleep(10)
                url = HAVANFarm.mails(mail, password)
                return url
            except ProxyError:
                raise ProxyError('Ошибка в прокси')

    @staticmethod
    def captcha2(name, api_key):
        for _ in range(3):
            try:
                captcha = {'2captcha.com': CaptchaSolvingService.TWOCAPTCHA,
                           'anti-captcha.com': CaptchaSolvingService.ANTI_CAPTCHA}
                with CaptchaSolver(captcha[name], api_key) as solver:
                    # solve CAPTCHA
                    solved = solver.solve_recaptcha_v2(
                        site_key="6Lc6yQIiAAAAAHSjSDbXJGDoDeZL7pRgB84xaUWG",
                        page_url="https://havah.io/"
                    )
                    # get response token
                    return solved.solution.token
            except BadInputDataError:
                pass

    @staticmethod
    def proxy_chrome(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
        manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
                """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%(host)s",
                    port: parseInt(%(port)d)
                  },
                  bypassList: ["foobar.com"]
                }
              };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%(user)s",
                    password: "%(pass)s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
            """ % {
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "user": PROXY_USER,
            "pass": PROXY_PASS,
        }

        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        co = Options()
        # extension support is not possible in incognito mode for now
        # co.add_argument('--incognito')
        co.add_argument('--disable-gpu')
        # disable infobars
        co.add_argument('--disable-infobars')
        co.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        # location of chromedriver, please change it according to your project.
        chromedriver = os.getcwd() + '/Chromedriver/chromedriver'
        co.add_extension(pluginfile)
        co.add_extension('HAVAH-Wallet.crx')
        driver = webdriver.Chrome(chromedriver, chrome_options=co)
        # return the driver with added proxy configuration.
        return driver

    def runs(self, button):
        self.driver.execute_script("arguments[0].click();", button)

    @staticmethod
    def proxy():
        with open('proxy.txt', 'r') as file:
            return file.read().splitlines()

    def reg_wallet(self):
        driver = self.driver
        driver.get('chrome-extension://cnncmdhjacpkmjmkcafchppbnpnhdmon/src/pages/popup/index.html')
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/button'))
        sleep(1)
        driver.find_element('xpath', '//*[@id=":r0:"]').send_keys('slava6680230')
        sleep(1)
        driver.find_element('xpath', '//*[@id=":r1:"]').send_keys('slava6680230')
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div/div[2]/div[1]/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[1]/div[2]/button'))
        sleep(1)
        root = tk.Tk()
        seeds = root.clipboard_get()
        return seeds

    def loads_wallet(self, seed_):
        driver = self.driver
        driver.get('chrome-extension://cnncmdhjacpkmjmkcafchppbnpnhdmon/src/pages/popup/index.html')
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/button'))
        sleep(1)
        self.driver.find_element('xpath', '//*[@id=":r0:"]').send_keys('slava6680230')
        sleep(0.5)
        driver.find_element('xpath', '//*[@id=":r1:"]').send_keys('slava6680230')
        sleep(0.5)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div/div[2]/div[2]/button'))
        sleep(1)
        driver.find_element('xpath', '//*[@id="outlined-multiline-static"]').send_keys(seed_)
        sleep(0.5)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/button'))
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/header/button[2]'))
        sleep(1)
        # runs(driver.find_element(By.XPATH, '//*[@id="mui-component-select-network"]'))
        driver.find_element(By.XPATH, '//*[@id="mui-component-select-network"]').click()
        sleep(1)
        self.runs(driver.find_element('xpath', '//*[@id="menu-network"]/div[3]/ul/li[2]'))

    def drive_click(self, text):
        self.driver.find_element("xpath", text).click()

    @staticmethod
    def mails(login, password):
        with MailBox('imap.rambler.ru').login(login, password) as mailbox:
            for _ in range(2):
                for msg in mailbox.fetch(AND(to=login, from_=('no-reply@havah.io'))):
                    if len(msg.html) > 0:
                        return msg.html.split('href="')[1].split('"')[0]
                sleep(5)
            with imaplib.IMAP4_SSL('imap.rambler.ru') as mail:
                mail.login(login, password)
                mail.list()
                mail.select("Spam")
                result, data = mail.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
                latest_email_uid = data[0].split()[-1]
                result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
                raw_email = data[0][1].decode('UTF-8')
                email_message = email.message_from_string(raw_email)
                for _ in range(5):
                    if 'no-reply@havah.io' in email.utils.parseaddr(email_message['From']):
                        return raw_email.split('<a target=3D"_blank" href=3D"') \
                                   [1].replace('\r', '').replace(' ', '').replace('3D', '').replace('\n', '') \
                                   .replace('=', '').split('pc')[0] + '=pc'
                    else:
                        sleep(3)

    @staticmethod
    def open_mail():
        with open('mail.txt', 'r') as file:
            file = file.read().splitlines()
            return [files.split(':') for files in file]

    def run(self):
        mails = self.open_mail()
        proxys = self.proxy()
        if len(mails) > len(proxys):
            raise 'Прокси меньше чем задано аккаунтов'
        for i, emails in enumerate(mails):
            proxy = proxys[i]
            proxy_separation = proxy.replace('@', ':').split(':')
            self.driver = self.proxy_chrome(PROXY_USER=proxy_separation[0], PROXY_PASS=proxy_separation[1],
                                            PROXY_HOST=proxy_separation[2], PROXY_PORT=int(proxy_separation[3]))
            self.driver.implicitly_wait(15)
            driver = self.driver
            driver.switch_to.window(driver.window_handles[0])
            url = self.post(emails[0], emails[1], self.captcha_name, self.API_key, proxy)
            print(url)
            seed = self.reg_wallet()
            adress = self.address_eth()
            Sv.logs(f'{seed} : {emails[0]}:{emails[1]} : {adress}')
            self.loads_wallet(seed)
            sleep(2)
            driver.get(url)
            sleep(5)
            driver.get(self.reff_url)
            read_mores = driver.find_elements("xpath", '//*[@id="root"]/div/div[2]/section[2]/h2')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            sleep(5)
            driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[3]/div[3]/button').click()

            sleep(2)
            driver.switch_to.window(driver.window_handles[2])
            sleep(1)
            self.runs(driver.find_element('xpath',
                                          '//*[@id="__root"]/main/section/div[2]/div[1]/div/label/span[1]/input'))
            sleep(1)
            self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div[2]/button[2]'))
            sleep(1)
            driver.switch_to.window(driver.window_handles[0])
            sleep(2)
            driver.find_element('xpath', '//*[@id="root"]/div/div[2]/section[2]/div[4]/div[3]/div').click()
            sleep(1)
            driver.find_element('xpath', '//*[@id="root"]/div/div[2]/section[2]/div[4]/div[3]/div/input') \
                .send_keys(emails[0][0].lower() + emails[0][1:])
            sleep(1)
            driver.find_element('xpath', '//*[@id="root"]/div/div[2]/section[2]/div[4]/div[3]/button[1]').click()
            sleep(2)
            read_mores = driver.find_elements("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[5]/div[2]')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            sleep(2)
            driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[5]/div[3]/button').click()
            sleep(20)
            driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[6]/div[3]/div/img[2]').click()
            sleep(1)
            driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[6]/div[3]/button').click()
            sleep(3)
            driver.switch_to.window(driver.window_handles[2])
            read_mores = driver.find_elements("xpath", '//*[@id="__root"]/main/section/div[2]/div/button[2]')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            sleep(2)
            self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div/button[2]'))
            sleep(5)
            driver.switch_to.window(driver.window_handles[0])
            read_mores = driver.find_elements("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[7]/div[2]')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            sleep(8)
            for _ in range(5):
                try:
                    driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[7]/div[3]/button/span').click()
                    break
                except ElementClickInterceptedException:
                    sleep(3)
            sleep(2)
            driver.switch_to.window(driver.window_handles[2])
            sleep(2)
            klick = ['//*[@id="root"]/div/section/div[1]/div[1]/div[2]/div[1]/div/div',
                     '//*[@id="root"]/div/section/div[1]/div[1]/div[2]/div[1]/div/ul/li[1]',
                     '//*[@id="root"]/div/section/div[1]/div[1]/div[2]/div[3]/div/button',
                     '//*[@id="modal-wrapper"]/div/div/div[2]/div[2]/div[1]/img']
            #

            for kl in klick:
                self.drive_click(kl)
                sleep(2)
            driver.switch_to.window(driver.window_handles[3])
            sleep(1)
            self.runs(
                driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div[1]/div/label/span[1]/input'))
            sleep(1)
            self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div[2]/button[2]'))
            sleep(2)
            driver.switch_to.window(driver.window_handles[2])
            klick = ['//*[@id="root"]/div/section/div[1]/div[3]/div[2]/div/button',
                     '//*[@id="scroll-id"]/div[1]/button',
                     '//*[@id="modal-wrapper"]/div/div/div[2]/div/div[2]/div[2]/div/button',
                     '//*[@id="root"]/div/section/div[3]/div/div[2]/div[1]/div/div',
                     '//*[@id="root"]/div/section/div[3]/div/div[2]/div[1]/div/ul/li[1]',
                     '//*[@id="root"]/div/section/div[3]/div/div[2]/div[3]/div/button',
                     '//*[@id="modal-wrapper"]/div/div/div[2]/div[1]/div[2]']
            for kl in klick:
                self.drive_click(kl)
                sleep(2)
            driver.find_element('xpath', '//*[@id="modal-wrapper"]/div/div/div[2]/div[2]/div/input') \
                .send_keys(adress)
            sleep(1)
            driver.find_element("xpath", '//*[@id="modal-wrapper"]/div/div/div[2]/div[3]/span').click()
            sleep(2)

            klick = ['//*[@id="root"]/div/section/div[4]/div/button',
                     '//*[@id="modal-shadow"]/div/div/div[2]/button[2]',
                     '//*[@id="root"]/div/section/div[2]/div[2]/div/button']
            for kl in klick:
                self.drive_click(kl)
                sleep(2)
            sleep(5)
            driver.switch_to.window(driver.window_handles[3])
            read_mores = driver.find_elements("xpath", '//*[@id="__root"]/main/section/div[2]/div/button[2]')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div/button[2]'))
            sleep(20)
            driver.switch_to.window(driver.window_handles[3])
            read_mores = driver.find_elements("xpath", '//*[@id="__root"]/main/section/div[2]/div/button[2]')
            for read_more in read_mores:
                driver.execute_script("arguments[0].scrollIntoView();", read_more)
            sleep(2)
            self.runs(driver.find_element('xpath', '//*[@id="__root"]/main/section/div[2]/div/button[2]'))
            sleep(15)
            driver.switch_to.window(driver.window_handles[0])
            while True:
                try:
                    driver.find_element("xpath", '//*[@id="root"]/div/div[2]/section[2]/div[8]/div[2]/button').click()
                    sleep(3)
                except:
                    break
            driver.quit()


def main():
    ref_url = input('Введите ваш рефф url')
    name_captcha = int(input('Какая у вас катча 1:2captcha.com, 2: anti-captcha 1/2: '))
    captha = {1: '2captcha.com', 2: 'anti-captcha.com'}
    api_key = input('Введите ваш API каптчи: ')
    hav = HAVANFarm(captha[name_captcha], api_key, ref_url)
    hav.run()


if __name__ == '__main__':
    main()

