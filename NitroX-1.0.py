from ctypes import windll
from os import system
from queue import Queue
from random import choices, choice
from string import ascii_letters, digits
from threading import Thread
from time import sleep

from colorama import Fore, init
from requests import get
from yaml import full_load

init()
default_values = '''checker:

  # Check for latest version of NitroX
  check_for_updates: true

  # Threads for checking Nitro codes
  threads: 200

  # Higher for better accuracy but slower (counted in milliseconds)
  timeout: 6000

  # Normal users should keep this false unless problem start happening
  debugging: false
  

  proxy:
    # Proxy types: https | socks4 | socks5
    proxy_type: 'socks4'
    # Proxy file name
    proxy_file: 'proxies.txt'
    
    # If proxy api link to be used.
    proxy_use_api: true
    # If proxy_use_api is true, put api link in the parentheses
    proxy_api_link: "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=3000"
    # If proxy_use_api is true, put a number for seconds to refresh the link (0 is for no refresh, recommend refresh: 300 seconds aka 5 minutes)
    refresh_api_link: 300

'''
while True:
    try:
        config = full_load(open('config.yml', 'r', errors='ignore'))
        break
    except FileNotFoundError:
        open('config.yml', 'w').write(default_values)
        system('cls')


class Main:
    def __init__(self):
        self.version = '1.0'
        tite = f'''{Fore.LIGHTCYAN_EX} _______  .__  __               ____  ___
 \      \ |__|/  |________  ____\   \/  /
 /   |   \|  \   __\_  __ \/  _ \\\     / 
/    |    \  ||  |  |  | \(  <_> )     \ 
\____|__  /__||__|  |__|   \____/___/\  \\
        \/                            \_/\n'''
        windll.kernel32.SetConsoleTitleW(f'NitroX-{self.version} | by ShadowOxygen')
        self.hits = 0
        self.checked = 0
        self.cpm = 0
        self.use_type = Checker.Proxy.type
        self.prints = Queue()
        self.header = {'Pragma': 'no-cache',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
        if Checker.version_check:
            try:
                gitversion = str(
                    get(url="https://raw.githubusercontent.com/ShadowOxygen/NitroX/master/version").text)
                if f'{self.version}\n' != gitversion:
                    print(tite)
                    print(f"{Fore.LIGHTRED_EX}Your version is outdated.")
                    print(
                        f"Your version: {self.version}\nLatest version: {gitversion}\nGet latest version in the link below")
                    print(
                        f"https://github.com/ShadowOxygen/NitroX/releases\nStarting in 5 seconds...{Fore.LIGHTCYAN_EX}")
                    sleep(5)
                    system('cls')
            except Exception as e:
                if Checker.debug:
                    print(f'\nError for updating checking:\n {e}\n')
                pass
        try:
            self.announcement = get(
                url='https://raw.githubusercontent.com/ShadowOxygen/NitroX/master/announcement').text
        except Exception as e:
            if Checker.debug:
                print(f'{Fore.LIGHTRED_EX}Error with announcement: {e}')
            self.announcement = ''
            pass
        print(tite)
        if not Checker.Proxy.proxy_use_api:
            while True:
                try:
                    self.proxies = open(Checker.Proxy.proxylist, 'r', encoding='u8', errors='ignore').read().split('\n')
                    print(Fore.LIGHTCYAN_EX)
                    break
                except FileNotFoundError:
                    print(
                        f'{Fore.LIGHTRED_EX}{Checker.Proxy.proxylist} not found, Please make sure {Checker.Proxy.proxylist} is in folder')
                    self.proxies = input('Please type the correct proxies file name: ')
                    continue
        elif Checker.Proxy.proxy_use_api:
            while True:
                try:
                    self.proxies = [x.strip() for x in get(url=Checker.Proxy.proxy_api).text.splitlines() if
                                    ':' in x and x != '']
                    if Checker.Proxy.refresh_api > 30:
                        Thread(target=self.refresh_api_link, daemon=True).start()
                    break
                except Exception as e:
                    if Checker.debug:
                        print(f'{Fore.LIGHTRED_EX}Error connecting with api link: {e}\n')
                    print(
                        f'{Fore.LIGHTRED_EX}Proxy Api link down or Connection Error\nPlease check your connection or make sure you entered the correct api link\n\nClosing program in 8 seconds...')
                    sleep(8)
                    exit()
        Thread(target=self.printing, daemon=True).start()
        Thread(target=self.cpmcounter, daemon=True).start()
        Thread(target=self.counter, daemon=True).start()
        print(self.announcement)
        for _ in range(Checker.threads):
            Thread(target=self.checking).start()

    def printing(self):
        while True:
            while self.prints.qsize() != 0:
                print(self.prints.get())

    def proxy_format(self):
        proxy = choice(self.proxies)
        if proxy.count(':') == 3:
            spl = proxy.split(':')
            proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
        else:
            proxy = proxy
        if self.use_type.lower() == 'http' or self.use_type.lower() == 'https':
            proxy_form = {
                'http': f"http://{proxy}",
                'https': f"https://{proxy}"
            }
        else:
            proxy_form = {
                'http': f"{self.use_type}://{proxy}",
                'https': f"{self.use_type}://{proxy}"
            }
        return proxy_form

    def counter(self):
        while True:
            if self.checked == 0:
                continue
            windll.kernel32.SetConsoleTitleW(
                f'NitroX-{self.version} | Hits: {self.hits}'
                f' | Checked: {self.checked}'
                f' | Chance: {self.hits}/{self.checked}'
                f' | CPM {self.cpm}')

    def refresh_api_link(self):
        while True:
            try:
                sleep(Checker.Proxy.refresh_api)
                self.proxies = [x.strip() for x in get(url=Checker.Proxy.proxy_api).text.splitlines() if ':' in x]
            except Exception as e:
                if Checker.debug:
                    print(f'{Fore.LIGHTRED_EX}Refreshing API link error: {e}')
                continue

    def cpmcounter(self):
        while True:
            while self.checked >= 1:
                now = self.checked
                sleep(4)
                self.cpm = (self.checked - now) * 15

    def checking(self):
        while True:
            code = ''.join(choices(ascii_letters + digits, k=16))
            req = self.check(code)
            self.checked += 1
            if req.__contains__('Unknown Gift Code'):
                continue
            elif req.__contains__('Nitro Monthly' or 'subscription_plan'):
                self.prints.put(f'{Fore.LIGHTGREEN_EX}HIT {code}{Fore.WHITE}')
                open('NitroHits.txt', 'a').write(f'https://discord.gift/{code}\n{req}\n')
                self.hits += 1

    def check(self, code):
        try:
            while True:
                try:
                    req = get(
                        url=f'https://discordapp.com/api/v6/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true',
                        proxies=self.proxy_format(), headers=self.header, timeout=Checker.timeout).text
                    if ('You are being rate limited.' or 'Access denied') in str(req):
                        continue
                    break
                except:
                    continue
            req = req
        except Exception as e:
            self.prints.put(f'{Fore.LIGHTRED_EX}\nError with check:\n {e}\n{Fore.WHITE}')
            req = 'Access denied'
        return req


class Checker:
    version_check = bool(config['checker']['check_for_updates'])
    threads = int(config['checker']['threads'])
    timeout = int(config['checker']['timeout']) / 1000
    debug = bool(config['checker']['debugging'])

    class Proxy:
        type = str(config['checker']['proxy']['proxy_type'])
        proxylist = str(config['checker']['proxy']['proxy_file'])
        proxy_use_api = bool(config['checker']['proxy']['proxy_use_api'])
        proxy_api = str(config['checker']['proxy']['proxy_api_link'])
        refresh_api = int(config['checker']['proxy']['refresh_api_link'])


if __name__ == '__main__':
    Main()
