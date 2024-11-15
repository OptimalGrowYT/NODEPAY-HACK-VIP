import asyncio
import cloudscraper
import json
import time
import uuid
import base64
from loguru import logger
from colorama import Fore, Style

PING_INTERVAL = 30 
RETRIES = 30000  
MAX_CONNECTIONS = 15 

DOMAIN_API = {
    "SESSION": "http://18.136.143.169/api/auth/session",
    "PING": "http://13.215.134.222/api/network/ping"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
account_info = {}

browser_id = {
    'ping_count': 0,
    'successful_pings': 0,
    'score': 0,
    'start_time': time.time(),
    'last_ping_status': 'Waiting...',
    'last_ping_time': None
}

# Base64 encoded banner string
encoded_banner = """
Ky0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSsKfCDilojilojilojilojilojilojilZcg4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVl+KWiOKWiOKVlyAgICDilojilojilojilZcgICDilojilojilojilZcg4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKVlyAgICAgfAp84paI4paI4pWU4pWQ4pWQ4pWQ4paI4paI4pWX4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4pWa4pWQ4pWQ4paI4paI4pWU4pWQ4pWQ4pWd4paI4paI4pWRICAgIOKWiOKWiOKWiOKWiOKVlyDilojilojilojilojilZHilojilojilZTilZDilZDilojilojilZfilojilojilZEgICAgIHwKfOKWiOKWiOKVkSAgIOKWiOKWiOKVkeKWiOKWiOKWiOKWiOKWiOKWiOKVlOKVnSAgIOKWiOKWiOKVkSAgIOKWiOKWiOKVkSAgICDilojilojilZTilojilojilojilojilZTilojilojilZHilojilojilojilojilojilojilojilZHilojilojilZEgICAgIHwKfOKWiOKWiOKVkSAgIOKWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKVkOKVnSAgICDilojilojilZEgICDilojilojilZEgICAg4paI4paI4pWR4pWa4paI4paI4pWU4pWd4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWR4paI4paI4pWRICAgICB8CnzilZrilojilojilojilojilojilojilZTilZ3ilojilojilZEgICAgICAgIOKWiOKWiOKVkSAgIOKWiOKWiOKVkSAgICDilojilojilZEg4pWa4pWQ4pWdIOKWiOKWiOKVkeKWiOKWiOKVkSAg4paI4paI4pWR4paI4paI4paI4paI4paI4paI4paI4pWXfAp8IOKVmuKVkOKVkOKVkOKVkOKVkOKVnSDilZrilZDilZ0gICAgICAgIOKVmuKVkOKVnSAgIOKVmuKVkOKVnSAgICDilZrilZDilZ0gICAgIOKVmuKVkOKVneKVmuKVkOKVnSAg4pWa4pWQ4pWd4pWa4pWQ4pWQ4pWQ4pWQ4pWQ4pWQ4pWdfAp8ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgfAp8IOKWiOKWiOKWiOKWiOKWiOKWiOKVlyDilojilojilojilojilojilojilZcgIOKWiOKWiOKWiOKWiOKWiOKWiOKVlyDilojilojilZcgICAg4paI4paI4pWXICAgIOKWiOKWiOKVlyAgIOKWiOKWiOKVl+KWiOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVlyAgfAp84paI4paI4pWU4pWQ4pWQ4pWQ4pWQ4pWdIOKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVlOKVkOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVkSAgICDilojilojilZEgICAg4pWa4paI4paI4pWXIOKWiOKWiOKVlOKVneKVmuKVkOKVkOKWiOKWiOKVlOKVkOKVkOKVnSAgfAp84paI4paI4pWRICDilojilojilojilZfilojilojilojilojilojilojilZTilZ3ilojilojilZEgICDilojilojilZHilojilojilZEg4paI4pWXIOKWiOKWiOKVkSAgICAg4pWa4paI4paI4paI4paI4pWU4pWdICAgIOKWiOKWiOKVkSAgICAgfAp84paI4paI4pWRICAg4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4paI4paI4pWRICAg4paI4paI4pWR4paI4paI4pWR4paI4paI4paI4pWX4paI4paI4pWRICAgICAg4pWa4paI4paI4pWU4pWdICAgICDilojilojilZEgICAgIHwKfOKVmuKWiOKWiOKWiOKWiOKWiOKWiOKVlOKVneKWiOKWiOKVkSAg4paI4paI4pWR4pWa4paI4paI4paI4paI4paI4paI4pWU4pWd4pWa4paI4paI4paI4pWU4paI4paI4paI4pWU4pWdICAgICAgIOKWiOKWiOKVkSAgICAgIOKWiOKWiOKVkSAgICAgfAp8IOKVmuKVkOKVkOKVkOKVkOKVkOKVnSDilZrilZDilZ0gIOKVmuKVkOKVnSDilZrilZDilZDilZDilZDilZDilZ0gIOKVmuKVkOKVkOKVneKVmuKVkOKVkOKVnSAgICAgICAg4pWa4pWQ4pWdICAgICAg4pWa4pWQ4pWdICAgICB8CistLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0r==
"""  # The base64-encoded string of your banner

def _banner():
    # Decode the base64 encoded banner
    decoded_banner = base64.b64decode(encoded_banner).decode()

    # Print the decoded banner
    print(Fore.WHITE + Style.BRIGHT + decoded_banner + Style.RESET_ALL)
    print(Fore.YELLOW + f" CREATED BY : DR ABDUL MATIN KARIMI: ⨭ {Fore.GREEN}https://t.me/doctor_amk")
    print(Fore.WHITE + f" DOWNLOAD LATEST HACKS HERE ➤ {Fore.GREEN}https://t.me/optimalgrowYT")
    print(Fore.RED  + f" LEARN HACKING HERE ➤ {Fore.GREEN}https://www.youtube.com/@optimalgrowYT/videos")
    print(Fore.YELLOW + f" PASTE YOUR (TOKEN) INTO TOKEN.TXT FILE AND PRESS START ")
    print(Fore.GREEN + f" ▀▄▀▄▀▄ 💲 𝗡𝗢𝗗𝗘𝗣𝗔𝗬 𝗔𝗜𝗥𝗗𝗥𝗢𝗣 𝗛𝗔𝗖𝗞 💲 ▄▀▄▀▄▀ ")
    log_line()

def log_line():
    print(Fore.GREEN + "-☠-" * 30 + Style.RESET_ALL)


def load_token():
    try:
        with open('Token.txt', 'r') as file:
            token = file.read().strip()
            return token
    except Exception as e:
        logger.error(f"Failed to load token: {e}")
        raise SystemExit("Exiting due to failure in loading token")

token_info = load_token()

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def uuidv4():
    return str(uuid.uuid4())

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp

async def render_profile_info(proxy):
    global account_info

    try:
        np_session_info = load_session_info(proxy)

        if not np_session_info:
            response = call_api(DOMAIN_API["SESSION"], {}, proxy)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(proxy, account_info)
                await start_ping(proxy)
            else:
                handle_logout(proxy)
        else:
            account_info = np_session_info
            await start_ping(proxy)
    except Exception as e:
        logger.error(f"Error in render_profile_info for proxy {proxy}: {e}")
        error_message = str(e)
        if any(phrase in error_message for phrase in [
            "sent 1011 (internal error) keepalive ping timeout; no close frame received",
            "500 Internal Server Error"
        ]):
            logger.info(f"Removing error proxy from the list: {proxy}")
            remove_proxy_from_list(proxy)
            return None
        else:
            logger.error(f"Connection error: {e}")
            return proxy

def call_api(url, data, proxy, token=None):
    headers = {
        "Authorization": f"Bearer {token or token_info}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://app.nodepay.ai/",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.nodepay.ai",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cors-site"
    }

    try:
        response = scraper.post(url, json=data, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        raise ValueError(f"Failed API call to {url}")

    return valid_resp(response.json())

async def start_ping(proxy):
    try:
        await ping(proxy)
        while True:
            await asyncio.sleep(PING_INTERVAL)
            await ping(proxy)
    except asyncio.CancelledError:
        logger.info(f"Ping task for proxy {proxy} was cancelled")
    except Exception as e:
        logger.error(f"Error in start_ping for proxy {proxy}: {e}")

async def ping(proxy):
    global RETRIES, status_connect

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time())
        }

        response = call_api(DOMAIN_API["PING"], data, proxy)
        if response["code"] == 0:
            logger.info(f"Ping successful via proxy {proxy}: {response}")
            RETRIES = 0
            status_connect = CONNECTION_STATES["CONNECTED"]
        else:
            handle_ping_fail(proxy, response)
    except Exception as e:
        logger.error(f"Ping failed via proxy {proxy}: {e}")
        handle_ping_fail(proxy, None)

def handle_ping_fail(proxy, response):
    global RETRIES, status_connect

    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout(proxy)
    elif RETRIES < 2:
        status_connect = CONNECTION_STATES["DISCONNECTED"]
    else:
        status_connect = CONNECTION_STATES["DISCONNECTED"]

def handle_logout(proxy):
    global token_info, status_connect, account_info

    token_info = None
    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    save_status(proxy, None)
    logger.info(f"Logged out and cleared session info for proxy {proxy}")

def load_proxies(proxy_file):
    try:
        with open(proxy_file, 'r') as file:
            proxies = file.read().splitlines()
        return proxies
    except Exception as e:
        logger.error(f"Failed to load proxies: {e}")
        raise SystemExit("Exiting due to failure in loading proxies")

def save_status(proxy, status):
    pass

def save_session_info(proxy, data):
    pass

def load_session_info(proxy):
    return {}

def is_valid_proxy(proxy):
    return True

def remove_proxy_from_list(proxy):
    pass

async def main():
    _banner()  # Display the banner
    with open('Proxy.txt', 'r') as f:
        all_proxies = f.read().splitlines()
    active_proxies = [proxy for proxy in all_proxies[:MAX_CONNECTIONS] if is_valid_proxy(proxy)]
    tasks = {asyncio.create_task(render_profile_info(proxy)): proxy for proxy in active_proxies}

    while True:
        done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        
        for task in done:
            failed_proxy = tasks[task]
            
            if task.result() is None:
                logger.info(f"Removing and replacing failed proxy: {failed_proxy}")
                active_proxies.remove(failed_proxy)
                
                if all_proxies:
                    new_proxy = all_proxies.pop(0)
                    if is_valid_proxy(new_proxy):
                        active_proxies.append(new_proxy)
                        new_task = asyncio.create_task(render_profile_info(new_proxy))
                        tasks[new_task] = new_proxy
            
            tasks.pop(task)

        while len(tasks) < MAX_CONNECTIONS and all_proxies:
            new_proxy = all_proxies.pop(0)
            if is_valid_proxy(new_proxy):
                active_proxies.append(new_proxy)
                new_task = asyncio.create_task(render_profile_info(new_proxy))
                tasks[new_task] = new_proxy

        await asyncio.sleep(3)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
