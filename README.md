# E2EE Terminal Chat (IRSSI Style)

Merhaba! Ben Halil. Bu benim kriptoloji destekli (uçtan uca şifreli - E2EE) IRSSI terminal deneyimim.

![Mr. Robot IRSSI Chat](<div class="tenor-gif-embed" data-postid="8435336107615142483" data-share-method="host" data-aspect-ratio="1" data-width="100%"><a href="https://tenor.com/view/worry-froge-froge-frog-frog-meme-hoodie-gif-8435336107615142483">Worry Froge Frog Meme Sticker</a>from <a href="https://tenor.com/search/worry+froge-stickers">Worry Froge Stickers</a></div> <script type="text/javascript" async src="https://tenor.com/embed.js"></script>)

## Neden Kriptolojili Yaptım?

Tamamen "öyle de diyebilirsin" tadında bir deneme. Gerçek ve güvenli bir iletişim ağının nasıl kurulabileceğini görmek istedim. İstemci-sunucu mimarisini asenkron (asyncio) yapıda kurgularken, araya AES-256 (CBC) simetrik şifrelemeyi katarak terminal tabanlı, tamamen şifreli ve IRSSI hissiyatı veren bir deneyim yaratmayı amaçladım.

Eğer biri aradaki ağı (network) dinlemeye kalkarsa, sadece anlamsız, karmaşık Base64 şifreli veriler görecektir.

## Nasıl Kullanılır?

Projenin çalışması için temel Python kütüphaneleri ve kriptografi eklentisine ihtiyacınız var.

### 1. Gereksinimleri Yükleme

Projeyi bilgisayarınıza indirdikten sonra, terminalde proje klasörünün içine girin ve gerekli kütüphaneleri yükleyin:

```bash
pip install cryptography
```
*(Windows kullanıcıları ayrıca `windows-curses` paketine ihtiyaç duyabilir: `pip install windows-curses`)*

### 2. Sunucuyu Başlatma

Önce dinleyici sunucuyu çalıştırmanız gerekiyor. Sunucu, istemcilerden (kullanıcılardan) gelen şifreli mesajları alıp diğerlerine dağıtmakla görevlidir.

```bash
python server.py
```

### 3. İstemcileri (Kullanıcıları) Bağlama

Sunucu çalıştıktan sonra, yeni bir terminal sekmesi (veya penceresi) açarak sohbete bağlanabilirsiniz. `client.py` dosyasını çalıştırırken bir kullanıcı adı belirlemeniz yeterlidir:

```bash
python client.py KullaniciAdiniz
```

*Not: Şifreleme (Encryption) için gerekli olan gizli anahtar (hex key), ilk girişte varsayılan olarak tanımlanmıştır.*

## Özellikler

- **Uçtan Uca Şifreleme (E2EE):** `cryptography` kütüphanesi ile AES-256 şifreleme.
- **Asenkron Yapı:** `asyncio` sayesinde aynı anda yüzlerce bağlantıyı engellemeden (non-blocking) yönetebilme.
- **Terminal Arayüzü:** `curses` kütüphanesi kullanılarak geliştirilmiş, retro IRSSI tarzı sohbet ekranı.
