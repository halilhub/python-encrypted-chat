import asyncio
import curses
import sys
import json
import time
from ui import ChatUI
from crypto import CryptoManager, generate_key_hex

class ChatClient:
    def __init__(self, stdscr, encryption_key: str, nickname: str, host='127.0.0.1', port=8888):
        self.ui = ChatUI(stdscr)
        self.crypto = CryptoManager(encryption_key)
        self.nickname = nickname
        self.host = host
        self.port = port
        self.writer = None

        # UI gönderme olayını bağla
        self.ui.on_message_send = self.handle_ui_send

        # Kullanıcı arayüzünden Ağa giden iletileri güvenli bir şekilde yönetmek için basit kuyruk
        self.outgoing_queue = asyncio.Queue()

    def handle_ui_send(self, message: str):
        # Curses bağlamından çağrıldığı için burada beklemiyoruz, 
        # ancak bunu olay döngüsünde zamanlayabiliriz
        # Bunun yerine, bir asyncio kuyruğuna koyup başka bir yerde işleyeceğiz
        pass # Daha iyi bir yol: doğrudan queue.put_nowait çağırın
    
    # Geri çağırmayı daha sonra asenkron bağlamda düzgün bir şekilde geçersiz kılalım.

    async def connect_to_server(self):
        self.ui.add_message(f"--- Bağlanılıyor: {self.host}:{self.port} ---")
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            self.writer = writer
            self.ui.add_message(f"--- Bağlandı! Şifreleme Etkin. ---")
            
            # UI döngüsünü, okuma döngüsünü ve yazma döngüsünü eşzamanlı olarak başlat
            await asyncio.gather(
                self.ui_loop(),
                self.read_loop(reader),
                self.write_loop()
            )
        except Exception as e:
            self.ui.add_message(f"--- Bağlantı Hatası: {e} ---")
            await asyncio.sleep(5)

    async def ui_loop(self):
        # Senkronize UI ve asenkronize Ağ arasında köprü kurmak için geri çağırmayı geçersiz kıl
        self.ui.on_message_send = lambda msg: self.outgoing_queue.put_nowait(msg)
        
        while True:
            self.ui.update()
            await asyncio.sleep(0.02) # ~50fps kullanıcı arayüzü güncelleme hızı
            
            # Çıkıp çıkmayacağımızı kontrol et (şimdilik kirli bir yöntem, belki /quit'i izleyebiliriz)
            if self.ui.input_buffer == "/quit":
                sys.exit(0)

    async def read_loop(self, reader):
        while True:
            try:
                data = await reader.readline()
                if not data:
                    self.ui.add_message("--- Sunucu bağlantısı koptu ---")
                    break
                
                # JSON'ı ayrıştır
                raw_json = data.decode('utf-8').strip()
                parsed = json.loads(raw_json)
                
                sender = parsed.get("sender", "Unknown")
                encrypted_payload = parsed.get("payload", "")
                
                # Şifreyi çöz
                decrypted = self.crypto.decrypt(encrypted_payload)
                self.ui.add_message(f"<{sender}> {decrypted}")

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.ui.add_message("--- Hatalı oluşturulmuş veri alındı ---")
            except Exception as e:
                self.ui.add_message(f"--- Okuma hatası: {e} ---")
                break

    async def write_loop(self):
        while True:
            # Kullanıcı arayüzünden bir mesaj bekle
            msg = await self.outgoing_queue.get()
            
            # Yerel olarak yazdır (şifrelenmemiş)
            self.ui.add_message(f"<{self.nickname}> {msg}")
            
            # Şifrele ve gönder
            encrypted = self.crypto.encrypt(msg)
            payload = {
                "sender": self.nickname,
                "payload": encrypted
            }
            json_payload = json.dumps(payload)
            
            if self.writer:
                try:
                    self.writer.write((json_payload + "\n").encode('utf-8'))
                    await self.writer.drain()
                except Exception as e:
                    self.ui.add_message(f"--- Yazma hatası: {e} ---")
                    break

def run_curses_app(stdscr, key, nickname, host, port):
    client = ChatClient(stdscr, key, nickname, host, port)
    asyncio.run(client.connect_to_server())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Eğer sağlanmamışsa yerel hata ayıklama için bir test anahtarı oluştur
        test_key = "d0121add1d8a1eef1038afac0d828a5598144caaccb6369c0d5071defcc64dfa"
        nickname = "TestUser"
        print(f"Kullanım: python client.py <kullanici_adi> <hex_anahtar> [sunucu_adresi] [port]")
        print(f"Varsayılan kullanıcı adı '{nickname}' ve test anahtarı kullanılıyor: {test_key}")
        time.sleep(2)  # Zaman modülünü kullanarak biraz bekletiyoruz
        key = test_key
        host = '127.0.0.1'
        port = 8888
    else:
        nickname = sys.argv[1]
        key = sys.argv[2]
        host = sys.argv[3] if len(sys.argv) > 3 else '127.0.0.1'
        port = int(sys.argv[4]) if len(sys.argv) > 4 else 8888

    from ui import ChatUI # yolda olduğundan emin olmak için
    try:
        curses.wrapper(run_curses_app, key, nickname, host, port)
    except KeyboardInterrupt:
        pass
