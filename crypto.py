import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Şimdilik basitlik açısından paylaşılan bir anahtarla simetrik şifreleme için AES-256 kullanacağız.
# 500'den fazla istemcisi olan gerçek dünya senaryosunda, her istemci sunucu ile
# bir oturum anahtarı müzakere eder (örn. Diffie-Hellman kullanarak) veya sunucu bir grup anahtarı dağıtır.
# Bu uygulama için, grup sohbeti maksadıyla önceden paylaşılan bir anahtarla başlayacağız.

class CryptoManager:
    def __init__(self, shared_key_hex: str):
        # Anahtar 32 baytlık (256 bit) bir onaltılık dize olmalıdır
        self.key = bytes.fromhex(shared_key_hex)
        if len(self.key) != 32:
            raise ValueError("Anahtar tam olarak 32 bayt (64 hex karakteri) olmalıdır")

    def encrypt(self, plaintext: str) -> str:
        """Bir metni şifreler ve IV + Şifreli Metin içeren base64 kodlu bir dize döndürür."""
        iv = os.urandom(16) # AES blok boyutu 128 bittir (16 bayt)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # PKCS7 dolgusu
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Şifreli metnin başına IV ekle ve base64 ile kodla
        encrypted_blob = iv + ciphertext
        return base64.b64encode(encrypted_blob).decode('utf-8')

    def decrypt(self, encrypted_b64: str) -> str:
        """IV + Şifreli Metin içeren base64 kodlu dizenin şifresini çözer."""
        try:
            encrypted_blob = base64.b64decode(encrypted_b64)
            iv = encrypted_blob[:16]
            ciphertext = encrypted_blob[16:]
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # PKCS7 dolgusunu kaldır
            unpadder = padding.PKCS7(128).unpadder()
            plaintext_bytes = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            # Şifre çözme başarısız olursa (yanlış anahtar, bozuk veri), bunu zarif bir şekilde yakalarız
            return f"<Şifreli Mesaj - Okunmuyor> (Hata: {str(e)})"

# Test için güvenli rastgele bir hex anahtarı oluşturmaya yarayan araç
def generate_key_hex() -> str:
    return os.urandom(32).hex()

if __name__ == "__main__":
    # Hızlı test
    my_key = generate_key_hex()
    print(f"Oluşturulan Anahtar (Bunu sunucu ve istemciler için saklayın!): {my_key}")
    
    crypto = CryptoManager(my_key)
    message = "Merhaba, gizli IRSSI dünyası!"
    print(f"Orijinal: {message}")
    
    enc = crypto.encrypt(message)
    print(f"Şifrelenmiş: {enc}")
    
    dec = crypto.decrypt(enc)
    print(f"Şifresi Çözülmüş: {dec}")
