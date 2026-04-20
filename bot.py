from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from base64 import urlsafe_b64decode
from datetime import datetime, timezone
from colorama import *
import asyncio, random, time, json, sys, re, os

class KieDex:
    def __init__(self) -> None:
        self.BASE_API = "https://ffcsrzbwbuzhboyyloam.supabase.co"
        self.APIKEY = "sb_publishable_ZN-MbrdVe1UcfCHwl-I2aw_DFZ2aWDf"

        self.USE_PROXY = False
        self.ROTATE_PROXY = False

        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.accounts = {}

        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}KieDex {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_accounts(self, new_accounts):
        filename = "accounts.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                email = new_acc["email"]

                if email in account_dict:
                    account_dict[email].update(new_acc)
                else:
                    account_dict[email] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def decode_token(self, email: str):
        try:
            access_token = self.accounts[email]["access_token"]
            header, payload, signature = access_token.split(".")
            decoded_payload = urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            user_id = parsed_payload["sub"]
            exp_time = parsed_payload["exp"]
            
            return {
                "user_id": user_id,
                "exp_time": exp_time
            }
        except Exception as e:
            return None
    
    def mask_account(self, account):
        try:
            if "@" in account:
                local, domain = account.split('@', 1)
                mask_account = local[:3] + '*' * 3 + local[-3:]
                return f"{mask_account}@{domain}"
            else:
                mask_account = account[:6] + '*' * 6 + account[-6:]
                return mask_account
        except Exception as e:
            return None
        
    def initialize_headers(self, email: str):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Apikey": self.APIKEY,
            "Authorization": f"Bearer {self.APIKEY}",
            "Cache-Control": "no-cache",
            "Origin": "https://kiedex.app",
            "Pragma": "no-cache",
            "Referer": "https://kiedex.app/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": self.accounts[email]["user_agent"],
            "X-Client-Info": "supabase-js-web/2.90.1"
        }

        return headers.copy()

    def generate_datetime(self):
        dt = datetime.now(timezone.utc)
        formatted = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        return formatted
    
    def generate_username(self, length=8):
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"

        username = []

        for i in range(length):
            if i % 2 == 0:
                username.append(random.choice(consonants))
            else:
                username.append(random.choice(vowels))

        return "".join(username)

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1  or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1  or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

    async def enusre_ok(self, response):
        if response.status >= 400:
            raise Exception(f"HTTP: {response.status}:{await response.text()}")

    async def check_connection(self, email: str, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=15)) as session:
                async with session.get(url=url, proxy=proxy, proxy_auth=proxy_auth) as response:
                    await self.enusre_ok(response)
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
    
    async def refresh_token(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/auth/v1/token"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Content-Type"] = "application/json;charset=UTF-8"
                headers["X-Supabase-Api-Version"] = "2024-01-01"
                params = {
                    "grant_type": "refresh_token"
                }
                payload = {
                    "refresh_token": self.accounts[email]["refresh_token"]
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, params=params, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Refreshing Tokens {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def user_profiles(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/profiles"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Accept"] = "application/vnd.pgrst.object+json"
                headers["Accept-Profile"] = "public"
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                params = {
                    "select": "*",
                    "user_id": f"eq.{self.accounts[email]['user_id']}"
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Profile :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def user_balances(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/balances"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Accept"] = "application/vnd.pgrst.object+json"
                headers["Accept-Profile"] = "public"
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                params = {
                    "select": "*",
                    "user_id": f"eq.{self.accounts[email]['user_id']}"
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Data {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_daily_faucet(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/rpc/claim_daily_usdt_faucet"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Profile"] = "public"
                headers["Content-Type"] = "application/json"
                payload = {
                    "p_claim_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Claim {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_daily_bonus(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/rpc/claim_daily_bonus"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Profile"] = "public"
                headers["Content-Type"] = "application/json"
                payload = {
                    "p_user_id": self.accounts[email]["user_id"],
                    "p_bonus_type": "DAILY_OIL",
                    "p_amount_oil": 40,
                    "p_claim_date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Bonus   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Claim {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def social_tasks(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/social_tasks"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Accept-Profile"] = "public"
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                params = {
                    "select": "*",
                    "is_active": "eq.true",
                    "order": "sort_order.asc"
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Social Tasks {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def tasks_progress(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/social_tasks_progress"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Accept-Profile"] = "public"
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                params = {
                    "select": "task_id,completed,claimed",
                    "user_id": f"eq.{self.accounts[email]['user_id']}"
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Progress Tasks {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def task_submissions(self, email: str, wallet_address: str, task_id: str, proof_type: str, proof_value: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/task_submissions"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Profile"] = "public"
                headers["Content-Type"] = "application/json"
                payload = {
                    "user_id": self.accounts[email]['user_id'],
                    "task_id": task_id,
                    "proof_type": proof_type,
                    "proof_value": proof_value,
                    "wallet_address": wallet_address,
                    "status": "completed"
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return True
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Start :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def update_tasks_progress(self, email: str, task_id: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/social_tasks_progress"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Profile"] = "public"
                headers["Content-Type"] = "application/json"
                payload = {
                    "user_id": self.accounts[email]['user_id'],
                    "task_id": task_id,
                    "completed": True,
                    "completed_at": self.generate_datetime()
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return True
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Start :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_social_task(self, email: str, task_id: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/rest/v1/rpc/claim_social_task_reward"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Profile"] = "public"
                headers["Content-Type"] = "application/json"
                payload = {
                    "p_task_id": task_id
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Claim :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def execute_trade(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/functions/v1/execute-trade"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(email)
                headers["Authorization"] = f"Bearer {self.accounts[email]['access_token']}"
                headers["Content-Type"] = "application/json"
                payload = {
                    "symbol": "ETHUSDT",
                    "side": "long",
                    "leverage": 5,
                    "margin": 5,
                    "takeProfitPrice": 2353.29,
                    "stopLossPrice": 2191.8
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Execute Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
            
    async def process_check_connection(self, email: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(email)

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True
            
            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(email)
                await asyncio.sleep(1)
                continue

            return False
            
    async def process_check_tokens(self, email: str, proxy_url=None):
        token_data = self.decode_token(email)
        if not token_data:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Invalid Token {Style.RESET_ALL}"
            )
            return False
        
        self.accounts[email]["user_id"] = token_data["user_id"]

        if int(time.time()) > token_data["exp_time"]:
            refresh = await self.refresh_token(email, proxy_url)
            if not refresh: return False

            self.accounts[email]["access_token"] = refresh.get("access_token")
            self.accounts[email]["refresh_token"] = refresh.get("refresh_token")

            account_data = [{
                "email": email,
                "access_token": self.accounts[email]["access_token"],
                "refresh_token": self.accounts[email]["refresh_token"]
            }]
            self.save_accounts(account_data)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Tokens Refreshed {Style.RESET_ALL}"
            )

        return True

    async def process_accounts(self, email: str, proxy_url=None):
        is_ok = await self.process_check_connection(email, proxy_url)
        if not is_ok: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(email)

        is_valid = await self.process_check_tokens(email, proxy_url)
        if not is_valid: return False

        profiles = await self.user_profiles(email, proxy_url)
        if profiles:
            username = profiles.get("username")
            wallet_address = profiles.get("linked_wallet_address")

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Username:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {username} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Wallet  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(wallet_address)} {Style.RESET_ALL}"
            )

        balances = await self.user_balances(email, proxy_url)
        if balances:
            kdx_balance = balances.get("kdx_balance", 0)
            kdx_claimable = balances.get("kdx_claimable", 0)
            demo_usdt_balance = balances.get("demo_usdt_balance", 0)
            base_eth_fee_balance = balances.get("base_eth_fee_balance", 0)
            oil_balance = balances.get("oil_balance", 0)

            self.log(f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}")
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{kdx_balance} KDX{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{demo_usdt_balance} USDT{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{oil_balance} OIL{Style.RESET_ALL}"
            )

        faucet = await self.claim_daily_faucet(email, proxy_url)
        if faucet:

            if faucet[0].get("success"):
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 100 USDT Claimed {Style.RESET_ALL}"
                )
            else:
                msg = faucet[0].get("message")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Faucet  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )

        bonus = await self.claim_daily_bonus(email, proxy_url)
        if bonus:

            if bonus[0].get("success"):
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Bonus   :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 40 OIL Claimed {Style.RESET_ALL}"
                )
            else:
                msg = bonus[0].get("message")
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Bonus   :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {msg} {Style.RESET_ALL}"
                )
            
        tasks = await self.social_tasks(email, proxy_url)
        if tasks:

            progress = await self.tasks_progress(email, proxy_url)
            if progress:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}")

                progress_map = {
                    item["task_id"]: item for item in progress
                }

                if not username:
                    username = self.generate_username()

                for task in tasks:
                    task_id = task["task_id"]
                    title = task["name"]
                    reward = task["reward"]
                    reward_type = task["reward_type"]
                    proof_type = task["proof_type"]

                    if proof_type == "none":
                        proof_value = f"auto:{self.accounts[email]['user_id']}:{task_id}"
                    else:
                        proof_value = f"@{username}"

                    prog = progress_map.get(task_id, {})

                    completed = prog.get("completed", False)
                    claimed = prog.get("claimed", False)

                    if claimed:
                        self.log(
                            f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                        )
                        continue

                    self.log(
                        f"{Fore.GREEN+Style.BRIGHT} ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                    )

                    if not completed:
                        start = await self.task_submissions(email, wallet_address, task_id, proof_type, proof_value, proxy_url)
                        if not start: continue

                        self.log(
                            f"{Fore.BLUE+Style.BRIGHT}   Start :{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                        )

                        update = await self.update_tasks_progress(email, task_id, proxy_url)
                        if not update: continue

                        self.log(
                            f"{Fore.BLUE+Style.BRIGHT}   Update:{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                        )

                    claim = await self.claim_social_task(email, task_id, proxy_url)
                    if not claim: continue

                    self.log(
                        f"{Fore.BLUE+Style.BRIGHT}   Claim :{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{reward} {reward_type.upper()}{Style.RESET_ALL}"
                    )
        
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No Accounts Loaded.{Style.RESET_ALL}")
                return

            self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if self.USE_PROXY: self.load_proxies()
        
                separator = "=" * 27
                for idx, account in enumerate(accounts, start=1):
                    email = account.get("email")
                    access_token = account.get("access_token")
                    refresh_token = account.get("refresh_token")

                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    if "@" not in email or not access_token or not refresh_token:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                        )
                        continue

                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Account:{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    if email not in self.accounts:
                        self.accounts[email] = {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user_agent": random.choice(self.USER_AGENTS)
                        }
                    
                    await self.process_accounts(email)
                    await asyncio.sleep(random.uniform(2.0, 3.0))

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*65)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = KieDex()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] KieDex - BOT{Style.RESET_ALL}                                       "                              
        )
        sys.exit(1)