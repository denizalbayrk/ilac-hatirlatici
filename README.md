# İlaç / Tedavi Saatleri Hatırlatıcı Planlayıcı

GEP1316 Kodlama Okuryazarlığı – Ara Değerlendirme Ödevi 1 (YZ Destekli Python Mini Uygulaması)

> **Uyarı:** Bu program tıbbi tavsiye vermez; yalnızca kullanıcının girdiği ilaç adı ve saatleri düzenler. Programa T.C. kimlik no, sağlık bilgisi gibi kişisel veri girmeyin.

## Ne yapar?
Düzenli ilaç kullanan (ya da bir yakınının ilaçlarını takip eden) kişi için komut satırında çalışan bir planlayıcıdır:

- İlaç adı, **ilk doz saati**, **günlük doz sayısı** ve **tedavi süresini** alır.
- Doz saatlerini 24 saate eşit bölerek hesaplar (ör. 08:00 başlangıç, günde 3 doz → 08:00, 16:00, 00:00).
- Bugünün planını zamana göre sıralı gösterir; dozları **ALINDI / GECİKTİ / YAKLAŞIYOR (≤30 dk) / BEKLİYOR** olarak etiketler ve sıradaki doz için hatırlatma verir.
- Verileri `ilaclar.csv` dosyasında saklar (program kapanıp açılınca kaybolmaz), günlük raporu `gunluk_plan.txt` dosyasına yazar.

## Nasıl çalıştırılır?
Gereksinim: Python 3.8+ (başka paket gerekmez).

```bash
python ilac_hatirlatici.py
```

Testleri çalıştırmak için:

```bash
python -m unittest -v
```

### Menü
| Seçim | İşlev |
|---|---|
| 1 | İlaç ekle (ad, ilk saat, günlük doz, gün sayısı) |
| 2 | İlaçları listele |
| 3 | Bugünün planı ve sıradaki doz hatırlatması |
| 4 | Doz alındı olarak işaretle |
| 5 | İlaç sil (onay sorulur) |
| 6 | Raporu `gunluk_plan.txt` dosyasına kaydet |
| 7 | Yeni güne geç (alınanlar sıfırlanır, kalan gün 1 azalır) |
| 0 | Çıkış |

## Ekran görüntüleri (gerçek çalıştırma çıktısı)

İlaç listesi:
```
  NO  İLAÇ                  DOZ SAATLERİ                KALAN GÜN  ALINAN
  ------------------------------------------------------------------------
  1   Parol                 08:00, 16:00, 00:00         7          0/3
  2   Antibiyotik           22:00, 10:00                5          0/2
```

Bugünün planı (saat 12:30 iken):
```
Şu an: 12:30
  SAAT   İLAÇ                    DURUM
  ---------------------------------------------
  08:00  Parol                   GECİKTİ
  16:00  Parol                   BEKLİYOR
  22:00  Antibiyotik             BEKLİYOR
  00:00  Parol                   BEKLİYOR
  10:00  Antibiyotik             BEKLİYOR
Sonraki doz: Parol saat 08:00 (4 sa 30 dk gecikti)
```

Hatalı girdilerde program çökmez, uyarı verip tekrar sorar:
```
İlaç adı:   ! Uyarı: Bu alan boş bırakılamaz.
İlk doz saati (SS:DD):   ! Uyarı: Saat 'SS:DD' biçiminde olmalı (örnek: 08:30, 00:00-23:59).
Günde kaç doz (1-12):   ! Uyarı: Sayı 1 ile 12 arasında olmalıdır.
Günde kaç doz (1-12):   ! Uyarı: Lütfen sayı giriniz (örnek: 3).
```

## Ödev gereksinimleri nerede karşılandı?
| # | Gereksinim | Karşılığı |
|---|---|---|
| 1 | ≥3 girdi + doğrulama | `metin_oku`, `saat_oku`, `tamsayi_oku`, `evet_mi` (4 çeşit girdi) |
| 2 | ≥2 karar yapısı | `durum_belirle` (if/elif/else), ana menü `if/elif/else`, tedavi bitti kontrolü |
| 3 | ≥1 döngü | Ana menü `while True`, doz hesaplama/plan `for` döngüleri |
| 4 | ≥3 fonksiyon | 25+ fonksiyon (ör. `doz_saatlerini_hesapla`, `gunluk_plan`, `sonraki_doz_bul`) |
| 5 | Liste/sözlük | İlaçlar = sözlüklerden oluşan liste |
| 6 | Biçimli çıktı + dosya | Hizalı tablolar, `ilaclar.csv`, `gunluk_plan.txt` |
| 7 | ≥5 test (≥2 hatalı girdi) | Aşağıdaki tablo ve `test_ilac_hatirlatici.py` (29 test) |
| 8 | GitHub: kod, README, PROMPTLAR | Bu depo |

## Test senaryoları (girdi → beklenen → gerçek)
`python -m unittest -v` çıktısı: **29 test, 29'u geçti (OK)**. Aşağıda öne çıkan senaryolar:

| # | Girdi | Beklenen | Gerçek | Tür |
|---|---|---|---|---|
| 1 | Saat `08:00` | 480 dakika (geçerli) | 480 | Normal |
| 2 | Saat `25:99` | Reddedilir (None) | None | **Hatalı girdi** |
| 3 | Saat `abc`, `08.00`, `08:5`, boş | Reddedilir | Hepsi None | **Hatalı girdi** |
| 4 | Saat `00:00` / `23:59` / `24:00` | 0 / 1439 / reddedilir | 0 / 1439 / None | **Uç değer** |
| 5 | Boş ya da 41 karakterlik ilaç adı | Uyarı verip tekrar sorar | Uyarı + tekrar sorar | **Hatalı girdi** |
| 6 | Günlük doz `0`, `-3`, `abc`, `13` | Her biri için uyarı, sonra `3` kabul | 4 uyarı, sonuç 3 | **Uç/hatalı girdi** |
| 7 | `08:00`, günde 3 doz | `08:00, 16:00, 00:00` | Aynı | Normal |
| 8 | Günde `0` doz hesabı | `ValueError` | `ValueError` | **Hatalı girdi** |
| 9 | Saat 23:30, 00:00 dozu bekliyor | `YAKLAŞIYOR`, "30 dk sonra" | Aynı | Uç (gece yarısı) |
| 10 | Doz tam 30 dk / 31 dk sonra | YAKLAŞIYOR / BEKLİYOR | Aynı | Uç değer |
| 11 | Tedavisi biten ilaç (kalan gün 0) | Plana girmez | Girmez | Uç |
| 12 | Aynı isimli ikinci ilaç (`parol`) | Eklenmez, uyarı | Eklenmedi | Hatalı girdi |
| 13 | Bozuk satırlı CSV (`99:99`, `abc`) | Bozuk satırlar atlanır | 2 satır atlandı | Hatalı veri |
| 14 | `ilaclar.csv` hiç yok | Boş liste, çökme yok | `[]` | Uç |

Bilinen sınırlama: plan, **ilk dozdan başlayan 24 saatlik bir döngü** olarak düşünülür. Örneğin 22:00 başlangıçlı ilacın "10:00" dozu ertesi güne aittir; "Yeni güne geç" ile bir sonraki döngü başlatılır.

## Dosyalar
- `ilac_hatirlatici.py` – uygulama
- `test_ilac_hatirlatici.py` – otomatik testler
- `PROMPTLAR.md` – YZ ile çalışma günlüğü (promptlar, kararlar)
- `RAPOR.md` – süreç belgesi, yansıtma ve YZ kullanım beyanı
