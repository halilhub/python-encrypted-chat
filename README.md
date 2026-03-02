# E2EE Terminal Chat (IRSSI Style)

Merhaba! Ben Halil. Bu benim kriptoloji destekli (uçtan uca şifreli - E2EE) IRSSI terminal deneyimim.

![Mr. Robot IRSSI Chat](https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NWJldGo2bWFuZzY1aWswMmlzeTJ1anFuN2YyaWEweDZwcm9yMDl4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/hIwx7v6vUUAUhHfl0c/giphy.gif)

## Neden Kriptolojili Yaptım?

Bu proje tamamen deneme amaçlı geliştirildi.
Amacım, gerçek ve güvenli bir iletişim ağının nasıl kurulabileceğini pratikte görmekti.
İstemci–sunucu mimarisini asenkron (asyncio) yapıda kurguladım ve iletişim katmanına AES-256 (CBC) simetrik şifreleme ekledim. Böylece terminal tabanlı, tamamen şifreli ve Irssi hissiyatı veren bir deneyim ortaya çıktı.

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
