
from pystyle import Colors, Colorate
import os
import re
import json
import time
import sys
import random
import requests
import threading
import gc
from typing import Dict, Any
import datetime

def show_banner():
    banner_text = """
===============================================================
🌟 TOOL GỬI TIN NHẮN TAG MESSENGER 🌟
📞 Contact: 0386449552
 © Copyright: MẬM BO ( BAN CAO )
===============================================================
"""
    print(Colorate.Vertical(Colors.rainbow, banner_text, 2))

def display_sandglass(delay):
    sys.stdout.write(Colorate.Horizontal(Colors.yellow_to_red, "[⌛] Đang chờ ", 1))
    for i in range(int(delay)):
        sys.stdout.write("⌛")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\033[0m\n")

class Mention:
    def __init__(self, thread_id, offset, length):
        self.thread_id = thread_id
        self.offset = offset
        self.length = length

    def _to_send_data(self, i):
        return {
            f"profile_xmd[{i}][id]": self.thread_id,
            f"profile_xmd[{i}][offset]": self.offset,
            f"profile_xmd[{i}][length]": self.length,
            f"profile_xmd[{i}][type]": "p",
        }

def send_typing_action(user_id, recipient_id, fb_dtsg, cookie):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(Colorate.Horizontal(Colors.yellow_to_red, f"[{now}] 💬 FAKE SOẠN TIN NHẮN tới {recipient_id}", 1))


    time.sleep(random.uniform(2.0, 3.0))

def get_uid_fbdtsg(ck):
    try:
        headers = {
            'Cookie': ck,
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get("https://mbasic.facebook.com", headers=headers)
        html = response.text

        user_id = re.search(r'c_user=(\d+)', ck)
        user_id = user_id.group(1) if user_id else None

        fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', html)
        fb_dtsg = fb_dtsg_match.group(1) if fb_dtsg_match else None

        if not user_id or not fb_dtsg:
            print("[❌] Không thể lấy user_id hoặc fb_dtsg.")
            return None, None, None, None, None

        return user_id, fb_dtsg, "123", "a", "1"
    except Exception as e:
        print(f"[❌] Lỗi khi lấy UID/fb_dtsg: {e}")
        return None, None, None, None, None

def get_info(uid, cookie):
    try:
        user_id, fb_dtsg, rev, req, a = get_uid_fbdtsg(cookie)
        if not user_id:
            return {"error": "Không thể lấy user ID"}

        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        form = {
            "ids[0]": uid,
            "fb_dtsg": fb_dtsg,
            "__a": a,
            "__req": req,
            "__rev": rev
        }

        res = requests.post("https://www.facebook.com/chat/user_info/", headers=headers, data=form)
        text = res.text[9:] if res.text.startswith("for (;;);") else res.text
        data = json.loads(text)

        profile = list(data["payload"]["profiles"].values())[0]
        return {
            "id": profile["id"],
            "name": profile.get("name", ""),
            "url": profile.get("uri", ""),
            "thumbSrc": profile.get("thumbSrc", ""),
            "gender": profile.get("gender", "")
        }
    except:
        return {"error": "Không thể lấy thông tin"}

def send_messages(user_id, fb_dtsg, rev, req, a, ck, idbox, uid, name, delay, stop_flag):
    if not os.path.exists("nhay.txt"):
        print("❌ Không tìm thấy file nhay.txt")
        return

    with open("nhay.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': ck,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.facebook.com',
        'Referer': f'https://www.facebook.com/messages/t/{idbox}'
    }

    while not stop_flag.is_set():
        for line in lines:
            if stop_flag.is_set():
                break

            tag_name = f"@{name}"
            if random.choice([True, False]):
                body = f"{tag_name} {line}"
                offset = 0
            else:
                body = f"{line} {tag_name}"
                offset = len(line) + 1

            mention = Mention(thread_id=uid, offset=offset, length=len(tag_name))
            ts = str(int(time.time() * 1000))

            payload = {
                "thread_fbid": idbox,
                "action_type": "ma-type:user-generated-message",
                "body": body,
                "client": "mercury",
                "author": f"fbid:{user_id}",
                "timestamp": ts,
                "offline_threading_id": ts,
                "message_id": ts,
                "source": "source:chat:web",
                "ephemeral_ttl_mode": "0",
                "__user": user_id,
                "__a": a,
                "__req": req,
                "__rev": rev,
                "fb_dtsg": fb_dtsg,
                "source_tags[0]": "source:chat"
            }

            payload.update(mention._to_send_data(0))

            send_typing_action(user_id, idbox, fb_dtsg, ck)

            try:
                requests.post("https://www.facebook.com/messaging/send/", headers=headers, data=payload)
                print(Colorate.Horizontal(Colors.green_to_cyan, f"[✔] Gửi: {body}", 1))
            except:
                print(Colorate.Horizontal(Colors.red_to_yellow, "[❌] Gửi lỗi", 1))

            del payload, mention
            gc.collect()

            for _ in range(int(delay * 10)):
                if stop_flag.is_set():
                    break
                time.sleep(0.1)

def main():
    try:
        show_banner()
        cookies_input = input("Nhập danh sách cookie Facebook (phân cách bằng dấu phẩy): ").strip()
        idboxes_input = input("Nhập danh sách ID Box cần gửi (phân cách bằng dấu phẩy): ").strip()
        uid = input("Nhập UID Người Cần Tag : ").strip()
        delay = float(input("Nhập số giây delay giữa mỗi tin nhắn (ví dụ: 5): "))

        cookies = [ck.strip() for ck in cookies_input.split(',') if ck.strip()]
        idboxes = [idb.strip() for idb in idboxes_input.split(',') if idb.strip()]

        if not cookies or not idboxes or not uid:
            print("Vui lòng nhập đầy đủ cookies, ID box và UID.")
            return

        user_data = get_info(uid, cookies[0])
        if "error" in user_data:
            print(f"Lỗi khi lấy tên người dùng: {user_data['error']}")
            return

        ten = user_data.get('name', 'N/A')
        print(Colorate.Horizontal(Colors.purple_to_blue, f"Tên Của UID | {ten}"))

        threads = []
        for ck in cookies:
            user_id, fb_dtsg, rev, req, a = get_uid_fbdtsg(ck)
            if not user_id or not fb_dtsg:
                print(f"[!] Cookie lỗi, bỏ qua.")
                continue

            for idbox in idboxes:
                stop_flag = threading.Event()
                thread = threading.Thread(
                    target=send_messages,
                    args=(user_id, fb_dtsg, rev, req, a, ck, idbox, uid, ten, delay, stop_flag)
                )
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
