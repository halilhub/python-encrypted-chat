import asyncio
import logging
import json
from datetime import datetime
from typing import Dict

# Temel loglamayı ayarla
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        # Aktif istemcileri takip et: {writer_objesi: istemci_adres_stringi}
        self.clients: Dict[asyncio.StreamWriter, str] = {} 

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logging.info(f"{addr} adresinden yeni bağlantı")
        
        # Yeni istemciyi kaydet
        self.clients[writer] = addr

        try:
            while True:
                # İstemciden bir satır oku (mesajlar yeni satır ile ayrılır)
                data = await reader.readline()
                if not data:
                    # Bağlantı istemci tarafından kapatıldı
                    break
                
                # Verinin şifrelenmiş yükü içeren JSON kodlu bir string olmasını bekliyoruz
                # Format: {"sender": "kullanici_adi", "payload": "base64_sifrelenmis_string"}
                message = data.decode('utf-8').strip()
                logging.info(f"{addr} adresinden ham veri alındı (Uzunluk: {len(message)})")
                
                # Mesajı diğer tüm istemcilere yayınla
                await self.broadcast(message, exclude_writer=writer)

        except ConnectionResetError:
            logging.warning(f"Bağlantı {addr} tarafından sıfırlandı")
        except Exception as e:
            logging.error(f"İstemci {addr} işlenirken hata: {e}")
        finally:
            self.remove_client(writer, addr)

    def remove_client(self, writer, addr):
        if writer in self.clients:
            del self.clients[writer]
        logging.info(f"İstemci ayrıldı: {addr} (Aktif kullanıcılar: {len(self.clients)})")
        writer.close()

    async def broadcast(self, message: str, exclude_writer=None):
        """Bağlı tüm istemcilere, isteğe bağlı olarak göndericiyi hariç tutarak bir mesaj gönderir."""
        disconnected_writers = []
        for writer, addr in self.clients.items():
            if writer != exclude_writer:
                try:
                    # Protokol için ayırıcı olarak yeni satır ekle
                    writer.write((message + '\n').encode('utf-8'))
                    await writer.drain() # Verinin gönderildiğinden emin ol
                except ConnectionError:
                    # Yazma başarısız olursa kaldırılmak üzere işaretle
                    disconnected_writers.append((writer, addr))
        
        # Bağlantısı kopan istemcileri temizle
        for writer, addr in disconnected_writers:
            self.remove_client(writer, addr)

    async def run_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        addr = server.sockets[0].getsockname()
        logging.info(f"{addr} üzerinde hizmet veriliyor")

        async with server:
            # Sonsuza kadar çalıştır
            await server.serve_forever()

if __name__ == "__main__":
    server = ChatServer(host='0.0.0.0', port=8888)
    try:
        logging.info("AsyncIO Sohbet Sunucusu Başlatılıyor (İşletim sistemi sınırlarına kadar eşzamanlılık)")
        asyncio.run(server.run_server())
    except KeyboardInterrupt:
        logging.info("Sunucu kapatılıyor.")
