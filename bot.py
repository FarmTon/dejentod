import os
import sys
import time
import json
import random
import argparse
import requests
from colorama import Fore, Style
from datetime import datetime
from urllib.parse import parse_qs
from base64 import urlsafe_b64decode

# Color settings
merah = Fore.LIGHTRED_EX
kuning = Fore.LIGHTYELLOW_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
putih = Fore.LIGHTWHITE_EX
hitam = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
line = putih + "~" * 50

class DejenTod:
    def __init__(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en,en-US;q=0.9",
            "Connection": "keep-alive",
            "Host": "api.djdog.io",
            "Origin": "https://djdog.io",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "X-Requested-With": "tw.nekomimi.nekogram",
        }
        self.marin_kitagawa = lambda data: {
            key: value[0] for key, value in parse_qs(data).items()
        }

    def http(self, url, headers, data=None):
        while True:
            try:
                now = datetime.now().isoformat(" ").split(".")[0]
                if data is None:
                    res = requests.get(url, headers=headers)
                elif data == "":
                    res = requests.post(url, headers=headers)
                else:
                    res = requests.post(url, headers=headers, data=data)
                with open("http.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"{now} - {res.status_code} {res.text}\n")
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                self.log(f"{merah}Connection error or timeout! Exception: {e}")
                time.sleep(5)  # Increased delay to handle persistent network issues
            except Exception as e:
                self.log(f"{merah}Unexpected error occurred: {e}")
                time.sleep(5)  # Increased delay for unexpected errors

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{hitam}[{now}] {msg}{reset}")

    def countdown(self, t):
        for i in range(t, 0, -1):
            menit, detik = divmod(i, 60)
            jam, menit = divmod(menit, 60)
            detik = str(detik).zfill(2)
            menit = str(menit).zfill(2)
            jam = str(jam).zfill(2)
            print(f"{putih}waiting {jam}:{menit}:{detik} ", flush=True, end="\r")
            time.sleep(1)

    def set_authorization(self, auth):
        self.headers["Authorization"] = auth

    def remove_authorization(self):
        if "Authorization" in self.headers:
            self.headers.pop("Authorization")

    def get_token(self, id):
        try:
            with open("tokens.json") as f:
                tokens = json.load(f)
            return tokens.get(str(id))
        except Exception as e:
            self.log(f"{merah}Failed to read tokens: {e}")
            return None

    def save_token(self, id, token):
        try:
            with open("tokens.json") as f:
                tokens = json.load(f)
            tokens[str(id)] = token
            with open("tokens.json", "w") as f:
                json.dump(tokens, f, indent=4)
        except Exception as e:
            self.log(f"{merah}Failed to save token: {e}")

    def is_expired(self, token):
        try:
            token = token.split(" ")[1]
            header, payload, sign = token.split(".")
            deload = urlsafe_b64decode(payload + "==").decode()
            jeload = json.loads(deload)
            now = datetime.now().timestamp()
            if now > jeload["exp"]:
                self.log(f"{merah}Token is expired!")
                return True
            return False
        except Exception as e:
            self.log(f"{merah}Failed to check token expiration: {e}")
            return True

    def login(self, data):
        url = "https://api.djdog.io/telegram/login?" + data
        self.remove_authorization()
        res = self.http(url, self.headers)
        if res.status_code != 200:
            self.log(f"{merah}Failed to fetch token, check http.log!")
            return None
        try:
            token = res.json()["data"]["accessToken"]
            self.log(f"{hijau}Successfully got token!")
            return token
        except Exception as e:
            self.log(f"{merah}Failed to parse token: {e}")
            return None

    def load_config(self, file):
        try:
            with open(file) as f:
                config = json.load(f)
            self.click_min = config["random_click"]["min"]
            self.click_max = config["random_click"]["max"]
            self.interval_click = config["interval_click"]
            self.auto_upgrade = config["auto_upgrade"]
            self.auto_buy_box = config["auto_buy_box"]
            self.var_countdown = config["countdown"]
        except Exception as e:
            self.log(f"{merah}Failed to load configuration: {e}")
            sys.exit()

    def account(self):
        info_url = "https://api.djdog.io/pet/information"
        adop_url = "https://api.djdog.io/pet/adopt"
        bar_url = "https://api.djdog.io/pet/barAmount"
        click_url = "https://api.djdog.io/pet/collect?clicks="
        boxmall_url = "https://api.djdog.io/pet/boxMall"
        levelup_url = "https://api.djdog.io/pet/levelUp/0"
        buybox_url = "https://api.djdog.io/pet/exchangeBox/0"

        while True:
            res = self.http(info_url, self.headers)
            if res.status_code != 200:
                self.log(f"{merah}Failed to get account information!")
                return False

            adopted = res.json()["data"]["adopted"]
            if not adopted:
                res = self.http(adop_url, self.headers, "")
                if res.status_code != 200:
                    self.log(f"{merah}Failed to adopt dog!")
                    return False
                self.log(f"{hijau}Successfully adopted a {biru}dog")
                continue

            break

        zawarudo = False
        while True:
            res = self.http(bar_url, self.headers)
            if res.status_code != 200:
                self.log(f"{merah}Failed to fetch bar information!")
                return

            data = res.json().get("data", {})
            avail = data.get("availableAmount", 0)
            gold = data.get("goldAmount", 0)
            level = data.get("level", 0)
            self.log(f"{putih}Level : {hijau}{level}")
            self.log(f"{hijau}Available energy : {putih}{avail}")
            self.log(f"{hijau}Total gold : {putih}{gold}")

            if zawarudo:
                return

            click_successful = False
            while avail > 0:
                click = random.randint(self.click_min, self.click_max)
                if click > avail:
                    click = avail
                res = self.http(f"{click_url}{click}", self.headers, "")
                if res.status_code != 200:
                    self.log(f"{merah}HTTP error occurred while sending click!")
                    continue

                retcode = res.json().get("returnCode")
                if retcode == 200:
                    avail -= click
                    self.log(f"{hijau}Successfully sent {putih}{click} {hijau}click{biru}, {hijau}energy : {putih}{avail}")
                    click_successful = True
                else:
                    self.log(f"{merah}Failed to send click, retrying...")
                    time.sleep(1)
                    
                if click_successful:
                    if avail <= 0:
                        break
                    self.countdown(self.interval_click)
                else:
                    self.log(f"{merah}Click operation failed repeatedly. Skipping account...")
                    return

            if self.auto_upgrade:
                upgrade_attempts = 0
                while upgrade_attempts < 5:  # Limit the number of upgrade attempts
                    res = self.http(boxmall_url, self.headers)
                    data = res.json().get("data", {})
                    gold = data.get("goldAmount", 0)
                    price_levelup = data.get("levelUpAmount", 0)
                    self.log(f"{hijau}Total gold : {putih}{gold}")
                    self.log(f"{biru}Upgrade price : {putih}{price_levelup}")
                    if gold > price_levelup:
                        res = self.http(levelup_url, self.headers, "")
                        retcode = res.json().get("returnCode")
                        if retcode == 200:
                            self.log(f"{biru}Level up {hijau}successfully")
                            upgrade_attempts = 0  # Reset attempts after a successful upgrade
                        else:
                            self.log(f"{merah}Level up failure, retrying...")
                            upgrade_attempts += 1
                            time.sleep(1)
                        continue
                    self.log(f"{kuning}Gold not enough to level up!")
                    break
            else:
                self.log(f"{putih}Auto upgrade disabled")

            if self.auto_buy_box:
                buy_box_attempts = 0
                while buy_box_attempts < 5:  # Limit the number of buy box attempts
                    res = self.http(boxmall_url, self.headers)
                    data = res.json().get("data", {})
                    gold = data.get("goldAmount", 0)
                    box_price = data.get("boxPrice", 0)
                    self.log(f"{hijau}Total gold : {putih}{gold}")
                    self.log(f"{biru}Box price : {putih}{box_price}")
                    if gold > box_price:
                        res = self.http(buybox_url, self.headers, "")
                        retcode = res.json().get("returnCode")
                        if retcode == 200:
                            self.log(f"{biru}Buy box {hijau}successfully!")
                            buy_box_attempts = 0  # Reset attempts after a successful purchase
                        else:
                            desc = res.json().get("returnDesc", "Unknown error")
                            self.log(f"{merah}{desc}")
                            buy_box_attempts += 1
                            time.sleep(1)
                        continue
                    self.log(f"{kuning}Gold not enough to buy box!")
                    break
            else:
                self.log(f"{putih}Auto buy box disabled")

            zawarudo = True

    def main(self):
        banner = f"""
    {hijau}Auto click for {biru}dejendogbot {hijau}Telegram
    
    {biru}By: {hijau}t.me/AkasakaID
    {biru}Github: {hijau}@AkasakaID
        
        """
        arg = argparse.ArgumentParser()
        arg.add_argument("--marinkitagawa", action="store_true")
        arg.add_argument("--data", default="data.txt")
        arg.add_argument("--config", default="config.json")
        args = arg.parse_args()
        if not args.marinkitagawa:
            os.system("cls" if os.name == "nt" else "clear")
        print(banner)
        if not os.path.exists("tokens.json"):
            with open("tokens.json", "w") as f:
                json.dump({}, f)
        self.load_config(args.config)
        try:
            with open(args.data) as f:
                datas = f.read().splitlines()
        except Exception as e:
            self.log(f"{merah}Failed to read data file: {e}")
            sys.exit()

        if len(datas) == 0:
            self.log(f"{merah}No account detected, add account to data.txt first!")
            sys.exit()

        self.log(f"{hijau}Total accounts : {putih}{len(datas)}")
        print(line)

        while True:
            for no, data in enumerate(datas):
                self.log(f"{hijau}Account number : {putih}{no + 1}{hijau}/{putih}{len(datas)}")
                parser = self.marin_kitagawa(data)
                user = json.loads(parser["user"])
                userid = user["id"]
                token = self.get_token(userid)
                if token is None:
                    token = self.login(data)
                    if token is None:
                        continue
                    self.save_token(userid, token)
                if self.is_expired(token):
                    token = self.login(data)
                    if token is None:
                        continue
                    self.save_token(userid, token)

                self.set_authorization(token)
                self.account()
                print(line)
            self.countdown(self.var_countdown)


if __name__ == "__main__":
    try:
        app = DejenTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1)
