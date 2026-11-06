# 🧪 STYX-LAB

<p align="center">
  <strong>Yerel Odaklı Siber Güvenlik Araştırma ve Eğitim Laboratuvarı</strong><br>
  Öğren. Analiz Et. Doğrula. Belgele.
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a> · <a href="README_TR.md">🇹🇷 Türkçe</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-14243A?style=for-the-badge&logo=python&logoColor=F2E8D5" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Platform-Linux-14243A?style=for-the-badge&logo=linux&logoColor=F2E8D5" alt="Linux">
  <img src="https://img.shields.io/badge/License-MIT-14243A?style=for-the-badge&logo=opensourceinitiative&logoColor=F2E8D5" alt="MIT Lisansı">
  <img src="https://img.shields.io/badge/Runtime%20Dependencies-None-14243A?style=for-the-badge&logo=python&logoColor=F2E8D5" alt="Harici bağımlılık yok">
</p>

<p align="center">
  <a href="https://github.com/raxwqx/STYX-LAB/actions/workflows/tests.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/raxwqx/STYX-LAB/tests.yml?branch=main&style=for-the-badge&label=Python%20CI&color=14243A&logo=githubactions&logoColor=F2E8D5" alt="Python CI">
  </a>
</p>

---

## ◈ Hakkında

**STYX-LAB**, uygulamalı, tekrarlanabilir ve sorumlu siber güvenlik öğrenimine odaklanan açık kaynaklı bir araştırma ve eğitim laboratuvarıdır.

Mevcut sürüm, Python ile geliştirilmiş yerel bir HTTP Security Headers ortamı sunar. Kullanıcıların iki sunucu yapılandırmasını karşılaştırmasına, HTTP yanıtlarını incelemesine, yerel değerlendirmeler yapmasına ve kanıta dayalı raporlar oluşturmasına olanak tanır.

> Davranışı anla. Kanıtı doğrula. Sonucu belgele.

## ✦ Proje Özellikleri

| Bileşen | Açıklama |
|:--|:--|
| 🖥️ Terminal Kontrol Paneli | Etkileşimli terminal arayüzü |
| 🌐 HTTP Güvenlik Laboratuvarı | İki profile sahip yerel HTTP sunucusu |
| 🔐 Güvenlik Başlıkları | Beş HTTP yanıt başlığının gösterimi |
| 📊 Değerlendirme Motoru | Yerel yapılandırma ve yanıt kontrolleri |
| 📁 Kanıt Raporları | JSON ve Markdown raporları |
| 🧪 Otomatik Testler | Birim ve entegrasyon testleri |
| ⚙️ GitHub Actions | Otomatik CI kontrolleri |

## 🔬 Mevcut Araştırma Senaryosu: HTTP Security Headers

STYX-LAB şu anda iki karşılaştırma profili içerir:

| Profil | Açıklama |
|:--|:--|
| `secure` | Yapılandırılmış eğitim güvenlik başlıklarını gönderir |
| `baseline` | Gösterilen beş güvenlik başlığını bilerek göndermez |

Gösterilen başlıklar:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `X-Frame-Options`

Her iki profil de `Cache-Control: no-store` kullanır. `baseline` profili yalnızca karşılaştırma içindir, üretim ortamı için değildir.

### Değerlendirme akışı

```text
       Laboratuvar profilini seç
                 |
                 v
        Yerel HTTP servisini başlat
                 |
                 v
          HTTP yanıtlarını incele
                 |
                 v
          Yerel değerlendirmeyi çalıştır
                 |
                 v
           Beklenen değerleri karşılaştır
                 |
                 v
              Kanıtları kaydet
                 |
            _____|_____
           |           |
           v           v
        JSON raporu  Markdown raporu
```

**Analist notu:** Başarılı bir değerlendirme yalnızca yerel laboratuvarın yapılan kontroller kapsamında beklendiği gibi davrandığını gösterir. Gerçek bir uygulamanın güvenli olduğunu kanıtlamaz.

## ⚡ Hızlı Başlangıç

### Gereksinimler

- Python 3.11 veya üzeri
- Linux veya desteklenen başka bir Python ortamı
- Terminal erişimi
- `curl` (isteğe bağlı)

Üçüncü taraf Python çalışma zamanı paketleri gerekli değildir.

### 1. Depoyu klonla

```bash
git clone https://github.com/raxwqx/STYX-LAB.git
cd STYX-LAB
```

### 2. Terminal kontrol panelini başlat

```bash
python3 lab/tui.py
```

### 3. Secure profilini doğrudan başlat

```bash
python3 lab/web/security_headers_lab.py --profile secure --port 8766
```

### 4. Yerel servisi incele

```bash
curl -i http://127.0.0.1:8766/
curl -i http://127.0.0.1:8766/health
curl -i http://127.0.0.1:8766/api/headers
```

### 5. Değerlendirme raporu oluştur

```bash
python3 -m lab.report --port 8766
```

Varsayılan rapor dosyaları:

```text
reports/
├── latest-assessment.json
└── latest-assessment.md
```

İşlem tamamlandığında sunucuyu `Ctrl+C` ile durdur.

## 🧭 Terminal Kontrol Paneli

Depo kök dizininde `python3 lab/tui.py` komutunu çalıştır.

| Tuş | İşlem |
|:--:|:--|
| `1` | Secure profilini başlat |
| `2` | Baseline profilini başlat |
| `3` | Otomatik testleri çalıştır |
| `4` | Yerel değerlendirme yap |
| `5` | Senaryo rehberini görüntüle |
| `0` | Çıkış |

Varsayılan portlar: secure `8766`, baseline `8765`.

İsteğe bağlı ayarlar:

```bash
STYXLAB_NO_ANIMATION=1 python3 lab/tui.py
NO_COLOR=1 python3 lab/tui.py
```

Başlangıçtaki kilit animasyonu yalnızca görsel markalamadır. Kimlik doğrulama veya erişim kontrolü sağlamaz.

## 📡 HTTP Uç Noktaları

| Uç Nokta | Metot | Amaç |
|:--|:--:|:--|
| `/` | GET | Eğitim ana sayfası |
| `/health` | GET | JSON servis durumu |
| `/api/headers` | GET | Aktif profil ve başlık metaverileri |
| Bilinmeyen yol | GET | JSON 404 yanıtı |

Dahil edilen servis `127.0.0.1` adresine bağlanır.

## 📑 Değerlendirme ve Raporlar

Değerlendirme aracı şunları kontrol eder:

1. Yerel servisin erişilebilirliği.
2. Health uç noktasının yanıtı.
3. Uç noktalar arasındaki profil tutarlılığı.
4. Güvenlik başlığı metaverileri.
5. Beş eğitim başlığının beklenen değerlere sahip olması veya baseline profilinde bulunmaması.

Geçerli ve eksiksiz bir yanıt normalde dokuz ayrı kontrol üretir.

| Durum | Anlamı |
|:--|:--|
| `PASS` | Beklenen yerel davranış gözlemlendi |
| `FAIL` | Bir veya daha fazla kontrol eşleşmedi |
| `UNAVAILABLE` | Gerekli yerel yanıt alınamadı veya ayrıştırılamadı |

Raporları farklı bir dizine kaydet:

```bash
python3 -m lab.report --port 8766 --output-dir reports/demo
```

Raporları yayımlamadan önce incele. Özel kalması gereken ortam bilgileri içerebilirler.

## 🧪 Testler

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q lab tests
```

GitHub Actions, Python 3.11, 3.12 ve 3.13 sürümlerinde otomatik kontroller gerçekleştirir.

[GitHub Actions sayfasını görüntüle](https://github.com/raxwqx/STYX-LAB/actions)

## 🏗️ Proje Yapısı

```text
STYX-LAB/
├── .github/workflows/tests.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── methodology/
│   └── scenarios/
├── lab/
│   ├── __init__.py
│   ├── report.py
│   ├── tui.py
│   └── web/
│       ├── __init__.py
│       └── security_headers_lab.py
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── README_TR.md
├── ROADMAP.md
└── SECURITY.md
```

## 🛡️ Kapsam ve Sorumlu Kullanım

STYX-LAB eğitim ve savunma odaklı bir güvenlik projesidir. Mevcut sürüm:

- `127.0.0.1` adresine bağlı yerel bir HTTP servisi kullanır.
- Yalnızca yerel STYX-LAB servisini değerlendirir.
- Harici sunucuları veya ağları taramaz.
- Uzak alan adlarını çözümlemez.
- Genel amaçlı bir güvenlik açığı tarayıcısı değildir.
- Herkese açık üretim ortamında çalıştırılmak için tasarlanmamıştır.

Güvenlik araçlarını yalnızca sahibi olduğun veya incelemek için açık izne sahip olduğun sistemlerde kullan. Ayrıntılar için [SECURITY.md](SECURITY.md) dosyasına bak.

## 🗺️ Yol Haritası

Gelecekte değerlendirilebilecek geliştirmeler arasında yeni savunma odaklı senaryolar, geliştirilmiş rapor metaverileri, daha iyi terminal erişilebilirliği ve test verilerinden oluşturulan örnek raporlar bulunur.

Bunlar geleceğe yönelik fikirlerdir, mevcut sürümde bulunan özellikler değildir. Güncel plan için [ROADMAP.md](ROADMAP.md) dosyasına bak.

---

## 🔭 Proje Vizyonu

STYX-LAB, mevcut HTTP Security Headers eğitim ortamının ötesine geçerek modüler bir siber güvenlik araştırma platformuna dönüşmek üzere tasarlanmaktadır.

Uzun vadeli vizyonumuz üç temel alana odaklanmaktadır:

### 🕵️ OSINT (Açık Kaynak İstihbaratı)
Herkese açık kaynaklardan bilgi toplama, düzenleme, ilişkilendirme ve analiz etme süreçlerini destekleyen araçlar ve iş akışları.

### 🔬 Dijital Adli Bilişim
Dijital kanıtların incelenmesi, dosya bütünlüğünün korunması, metadata analizi, zaman çizelgelerinin oluşturulması ve bulguların belgelenmesine yönelik yetenekler.

### 🛡️ Siber Güvenlik Laboratuvarı
Siber güvenlik kavramlarını öğrenmek, test etmek ve anlamak için tasarlanmış izole eğitim ortamları ve uygulamalı araçlar.

### Amacımız

OSINT, dijital adli bilişim ve siber güvenlik araştırmalarını tek bir modüler platformda bir araya getirmek. Bu süreçte şeffaflık, tekrarlanabilir araştırma, sorumlu kullanım ve açık kaynak geliştirme ilkelerini esas almak.

**Geliştirme notu:** Bunlar STYX-LAB'in uzun vadeli hedefleridir. Mevcut sürüm HTTP Security Headers eğitimi ve değerlendirmesine odaklanmaktadır. Yeni yetenekler geliştirildikçe aşamalı olarak projeye eklenecek ve belgelenecektir.

## 🤝 Katkıda Bulunma

Katkılar memnuniyetle karşılanır.

1. [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını oku.
2. Deneylerini yerel, kapsamı belirli ve tekrarlanabilir tut.
3. Yeni davranışlar için test ekle.
4. Kimlik bilgilerini veya özel bilgileri depoya gönderme.

## 📜 Lisans

STYX-LAB, [MIT Lisansı](LICENSE) altında yayımlanır.

---

<p align="center">
  <strong>STYX-LAB</strong><br>
  <sub>Sorumlu araştır. Dikkatli incele. Açık geliştir.</sub><br><br>
  <a href="https://github.com/raxwqx/STYX-LAB">GitHub Deposu</a> ·
  <a href="https://github.com/raxwqx">Geliştirici Profili</a>
</p>
