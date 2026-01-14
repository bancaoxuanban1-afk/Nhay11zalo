import multiprocessing
import time
import random
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.box import DOUBLE
from rich.table import Table
from zlapi import ZaloAPI, ZaloAPIException, Message, ThreadType

console = Console()

def console_print(text, style="white"):
    console.print(text, style=style)

def create_main_banner():
    banner = Text(justify="center")
    banner.append("""
╔═╗╔═╦═══╦═╗╔═╗╔══╗╔═══╗
║║╚╝║║╔═╗║║╚╝║║║╔╗║║╔═╗║
║╔╗╔╗║║─║║╔╗╔╗║║╚╝╚╣║─║║
║║║║║║╚═╝║║║║║║║╔═╗║║─║║
║║║║║║╔═╗║║║║║║║╚═╝║╚═╝║
╚╝╚╝╚╩╝─╚╩╝╚╝╚╝╚═══╩═══╝
╔═╗╔═╗╔════╦═══╦═══╦╗───
╚╗╚╝╔╝║╔╗╔╗║╔═╗║╔═╗║║───
─╚╗╔╝─╚╝║║╚╣║─║║║─║║║───
─╔╝╚╗───║║─║║─║║║─║║║─╔╗
╔╝╔╗╚╗──║║─║╚═╝║╚═╝║╚═╝║
╚═╝╚═╝──╚╝─╚═══╩═══╩═══╝
""", style="cyan")
    banner.append("\n🌟 TOOL TREO NHÂY 11 ZALO BY MẬM BO ( BAN CAO )🌟\n", style="magenta")
    banner.append("👑 Admin: Mậm Bo \n", style="magenta")
    banner.append("📱 Thông tin liên hệ:\n", style="blue")
    banner.append("   • Zalo: 0386449552\n", style="cyan")
    banner.append("\nℹ️ Phiên bản: v10.8\n", style="cyan")
    banner.append(f"⏰ Thời gian: {time.strftime('%I:%M %p, %d/%m/%Y')}\n", style="blue")
    banner.append("🔄 Cập nhật lần cuối: 25/12/2025\n", style="blue")
    banner.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style="cyan")
    banner.append("🚀 Chúc bạn nhây vui vẻ!\n", style="cyan")
    banner.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="cyan")
    return banner

def create_instructions_panel():
    instructions = Text(justify="left")
    instructions.append("🔹 HƯỚNG DẪN SỬ DỤNG TOOL TREO NHÂY 11 🔹\n", style="bold cyan")
    instructions.append("1️⃣ Nhập số lượng tài khoản Zalo muốn chạy.\n", style="white")
    instructions.append("2️⃣ Nhập IMEI, Cookie cho từng tài khoản.\n", style="white")
    instructions.append("3️⃣ Chọn nhiều bạn bè để spam (VD: 1,2,3).\n", style="white")
    instructions.append("4️⃣ Chọn delay cố định hoặc random (Y/N).\n", style="white")
    instructions.append("5️⃣ Nếu random, nhập khoảng delay min và max.\n", style="white")
    instructions.append("📌 Lưu ý: Đảm bảo file nhaychet.txt chứa nội dung và cookie hợp lệ!\n", style="bold blue")
    return Panel(instructions, title="Hướng Dẫn Sử Dụng", border_style="cyan", box=DOUBLE, width=60, padding=(0, 1))

def read_file_content(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        console_print(f"[❌] Lỗi đọc file {filename}: {e}", style="bold magenta")
        return []

def parse_selection(input_str, max_index):
    try:
        numbers = [int(i.strip()) for i in input_str.split(',')]
        return [n for n in numbers if 1 <= n <= max_index]
    except:
        console_print("[❌] Định dạng không hợp lệ!", style="bold magenta")
        return []

class Bot(ZaloAPI):
    def __init__(self, imei, session_cookies, delay_min=0, delay_max=None, friend_ids=None):
        super().__init__('api_key', 'secret_key', imei, session_cookies)
        self.delay_min = delay_min
        self.delay_max = delay_max if delay_max is not None else delay_min
        self.friend_ids = friend_ids or []
        self.message_lines = read_file_content("nhayhoa.txt")
        self.running_flags = {}
        self.processes = {}

    def start_spam(self, thread_id, thread_type):
        if not self.message_lines:
            console_print("[❌] File nhaychet.txt rỗng hoặc không đọc được!", style="bold magenta")
            return
        if thread_id not in self.running_flags:
            self.running_flags[thread_id] = multiprocessing.Value('b', False)
        if thread_id not in self.processes:
            self.processes[thread_id] = None
        if not self.running_flags[thread_id].value:
            self.send(Message(text=""), thread_id, thread_type, ttl=60000)
            self.running_flags[thread_id].value = True
            self.processes[thread_id] = multiprocessing.Process(
                target=self.spam_messages_friend,
                args=(thread_id, thread_type, self.running_flags[thread_id])
            )
            self.processes[thread_id].start()

    def spam_messages_friend(self, thread_id, thread_type, running_flag):
        while running_flag.value:
            if not self.message_lines:
                self.message_lines = read_file_content("nhayhoa.txt")
                if not self.message_lines:
                    console_print("[❌] File nhaychet.txt rỗng!", style="bold magenta")
                    running_flag.value = False
                    break
            raw_msg = random.choice(self.message_lines)
            try:
                user_info = self.fetchUserInfo(thread_id)
                if not user_info or thread_id not in user_info.changed_profiles:
                    console_print(f"[⚠️] Bạn bè {thread_id} không hợp lệ!", style="bold blue")
                    running_flag.value = False
                    break
                user_name = user_info.changed_profiles[thread_id]['displayName']
                self.setTyping(thread_id, thread_type)
                time.sleep(0.1)
                self.send(Message(text=raw_msg), thread_id=thread_id, thread_type=thread_type)
                
            except Exception as e:
                console_print(f"[❌] Lỗi gửi tin nhắn: {e}", style="bold magenta")
                time.sleep(3)
                continue
            delay = random.uniform(self.delay_min, self.delay_max)
            
            time.sleep(delay)

    def onMessage(self, *args, **kwargs):
        pass

    def onEvent(self, *args, **kwargs):
        pass

    def onAdminMessage(self, *args, **kwargs):
        pass

    def fetch_friends(self):
        try:
            friends = self.fetchAllFriends()
            friend_list = []
            for friend in friends:
                friend_list.append({
                    'id': friend.userId,
                    'name': friend.displayName
                })
            return friend_list
        except Exception as e:
            console_print(f"[❌] Lỗi lấy danh sách bạn bè: {e}", style="bold magenta")
            return []

def start_bot_spam11(imei, session_cookies, delay_min, delay_max, friend_ids):
    bot = Bot(imei, session_cookies, delay_min=delay_min, delay_max=delay_max, friend_ids=friend_ids)
    for friend_id in friend_ids:
        console_print(f"[▶️] Bắt đầu spam 11 bạn bè {friend_id}", style="bold cyan")
        bot.start_spam(friend_id, ThreadType.USER)
    bot.listen(run_forever=True, thread=False, delay=1, type='requests')

def start_multiple_accounts():
    while True:
        console.clear()
        console.print(Panel(create_main_banner(), title="Tool Treo Nhây 11", border_style="cyan", box=DOUBLE, width=60, padding=(0, 1)))
        console.print(create_instructions_panel())
        try:
            num_accounts = int(Prompt.ask("[💠] Nhập số lượng tài khoản Zalo muốn chạy", default="1"))
        except ValueError:
            console_print("[❌] Nhập sai, phải là số nguyên!", style="bold magenta")
            continue
        processes = []
        for i in range(num_accounts):
            console.print(f"\n[🔹] Nhập thông tin cho tài khoản {i+1} [🔹]", style="bold cyan")
            try:
                imei = Prompt.ask("[📱] Nhập IMEI của Zalo")
                cookie_str = Prompt.ask("[🍪] Nhập Cookie")
                try:
                    session_cookies = eval(cookie_str)
                    if not isinstance(session_cookies, dict):
                        console_print("[❌] Cookie phải là dictionary!", style="bold magenta")
                        continue
                except:
                    console_print("[❌] Cookie không hợp lệ, dùng dạng {'key': 'value'}!", style="bold magenta")
                    continue
                bot = Bot(imei, session_cookies)
                delay_type = Prompt.ask("[⏳] Delay cố định hay random? (Y/N)", default="N").lower()
                if delay_type == 'y':
                    while True:
                        try:
                            delay_min = float(Prompt.ask("[⏳] Nhập delay ít nhất (giây)", default="0"))
                            if delay_min < 0:
                                console_print("[❌] Delay min phải không âm!", style="bold magenta")
                                continue
                            break
                        except ValueError:
                            console_print("[❌] Delay min phải là số!", style="bold magenta")
                    while True:
                        try:
                            delay_max = float(Prompt.ask("[⏳] Nhập delay nhiều nhất (giây)", default="5"))
                            if delay_max < delay_min:
                                console_print("[❌] Delay max phải lớn hơn hoặc bằng delay min!", style="bold magenta")
                                continue
                            break
                        except ValueError:
                            console_print("[❌] Delay max phải là số!", style="bold magenta")
                else:
                    while True:
                        try:
                            delay_min = float(Prompt.ask("[⏳] Nhập delay cố định (giây)", default="5"))
                            if delay_min < 0:
                                console_print("[❌] Delay phải không âm!", style="bold magenta")
                                continue
                            break
                        except ValueError:
                            console_print("[❌] Delay phải là số!", style="bold magenta")
                    delay_max = delay_min
                friends = bot.fetch_friends()
                if not friends:
                    console_print("[⚠️] Không lấy được bạn bè nào!", style="bold blue")
                    continue
                table = Table(show_header=True, header_style="bold cyan", show_lines=False, box=None)
                table.add_column("STT", width=5, justify="center", style="white")
                table.add_column("Tên bạn bè", width=25, justify="left", style="bold cyan")
                table.add_column("ID", width=15, justify="left", style="blue")
                for idx, friend in enumerate(friends, 1):
                    table.add_row(str(idx), friend['name'], friend['id'])
                console.print(Panel(table, title="[bold cyan]📋 Danh sách bạn bè[/bold cyan]", border_style="cyan", width=60, padding=(0, 1)))
                raw = Prompt.ask("[🔸] Nhập số thứ tự bạn bè để spam (VD: 1,2,3)", default="")
                selected = parse_selection(raw, len(friends))
                if not selected:
                    console_print("[⚠️] Không chọn bạn bè nào!", style="bold blue")
                    continue
                friend_ids = [friends[i - 1]['id'] for i in selected]
                p = multiprocessing.Process(
                    target=start_bot_spam11,
                    args=(imei, session_cookies, delay_min, delay_max, friend_ids)
                )
                processes.append(p)
                p.start()
            except Exception as e:
                console_print(f"[❌] Lỗi nhập liệu: {e}", style="bold magenta")
                continue
        console_print("\n[✅] TẤT CẢ BOT ĐÃ KHỞI ĐỘNG THÀNH CÔNG", style="bold cyan")
        while True:
            restart = Prompt.ask("[🔄] Bạn muốn dùng lại tool? (Y/N)", default="N").strip().lower()
            if restart in ['y', 'n']:
                break
            console_print("[!] Vui lòng nhập Y hoặc N!", style="bold magenta")
        if restart == 'y':
            continue
        else:
            console_print("\n👋 Chào tạm biệt! Cảm ơn bạn đã sử dụng tool!", style="bold magenta")
            break

if __name__ == "__main__":
    start_multiple_accounts()
