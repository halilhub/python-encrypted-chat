import curses
import time
from typing import Callable, Optional

class ChatUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(1) # İmleci göster
        self.stdscr.nodelay(True) # Bloklamayan girdi
        
        # Boyutlar
        y, x = self.stdscr.getmaxyx()
        self.max_y: int = int(y)
        self.max_x: int = int(x)
        
        # Pencereler
        # Sohbet geçmişi alanı: girdi alanı için 2 satır hariç yukarıdan aşağıya
        self.chat_win = curses.newwin(self.max_y - 2, self.max_x, 0, 0)
        self.chat_win.scrollok(True)
        
        # Ayırıcı çizgi
        self.sep_win = curses.newwin(1, self.max_x, self.max_y - 2, 0)
        self.sep_win.bkgd(' ', curses.A_REVERSE)
        self.sep_win.addstr(0, 0, " [Şifreli IRSSI Sohbeti] ")
        self.sep_win.noutrefresh()
        
        # Girdi alanı
        self.input_win = curses.newwin(1, self.max_x, self.max_y - 1, 0)
        
        self.input_buffer = ""
        self.messages = []
        
        # Geri çağrımlar
        self.on_message_send: Optional[Callable[[str], None]] = None

    def draw_messages(self):
        self.chat_win.clear()
        # Mesajları aşağıdan yukarıya göster veya yazdırıp kaydırmasını sağla
        # Aslında sadece ekleyip scrollok'un kaydırmayı halletmesini sağlamak daha kolay
        # Bekle, eğer temizlersek her şeyi yeniden çizmemiz gerekir.
        # Sadece ekrana sığan son N mesajı yeniden çizelim.
        max_lines = self.max_y - 2
        start_idx = int(max(0, len(self.messages) - max_lines))
        display_msgs = self.messages[start_idx:]
        
        for i, msg in enumerate(display_msgs):
            if i < max_lines:
                # max_x'ten uzun satırları ele al (şimdilik basit kırpma, 
                # gerçek bir uygulamada metni kaydırırdık)
                safe_msg = msg[:self.max_x-1]
                self.chat_win.addstr(i, 0, safe_msg)
        self.chat_win.noutrefresh()

    def add_message(self, message: str):
        self.messages.append(message)
        self.draw_messages()
        self.refresh_input()

    def refresh_input(self):
        self.input_win.clear()
        prompt = "> "
        safe_input = self.input_buffer[-(self.max_x - len(prompt) - 1):]
        self.input_win.addstr(0, 0, prompt + safe_input)
        self.input_win.noutrefresh()

    def handle_input(self):
        try:
            char = self.stdscr.getch()
        except curses.error:
            return

        if char == -1:
            return

        if char in (curses.KEY_ENTER, 10, 13):
            if self.input_buffer.strip():
                if self.on_message_send:
                    self.on_message_send(self.input_buffer)
                self.input_buffer = ""
        elif char in (curses.KEY_BACKSPACE, 127, 8):
            self.input_buffer = self.input_buffer[:-1]
        elif 32 <= char <= 126: # Yazdırılabilir karakterler
            self.input_buffer += chr(char)
            
        self.refresh_input()

    def update(self):
        """Kullanıcı arayüzü güncellemelerini işlemek için ana döngüde sürekli çağrılır."""
        # Terminal boyutlandırmasını ele al
        new_y, new_x = self.stdscr.getmaxyx()
        if int(new_y) != self.max_y or int(new_x) != self.max_x:
            self.max_y, self.max_x = int(new_y), int(new_x)
            curses.resizeterm(self.max_y, self.max_x)
            
            self.chat_win.resize(self.max_y - 2, self.max_x)
            self.sep_win.resize(1, self.max_x)
            self.sep_win.mvwin(self.max_y - 2, 0)
            self.sep_win.clear()
            self.sep_win.bkgd(' ', curses.A_REVERSE)
            title = " [Şifreli IRSSI Sohbeti] "
            self.sep_win.addstr(0, 0, title[:self.max_x-1])
            self.sep_win.noutrefresh()
            
            self.input_win.resize(1, self.max_x)
            self.input_win.mvwin(self.max_y - 1, 0)
            
            self.draw_messages()

        self.handle_input()
        curses.doupdate()

