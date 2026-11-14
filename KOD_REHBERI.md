# Kod Rehberi – `ilac_hatirlatici.py` (sözlü doğrulama hazırlığı)

Satır numaraları `ilac_hatirlatici.py` içindir. Her bölümde önce "ne işe yarar", sonra "satır satır ne olur" yazılıdır.

## Büyük resim
Program bir **menü döngüsüdür** (`main`, satır 381). İlaçlar bellekte bir **liste** olarak durur; listedeki her eleman bir **sözlüktür**:
`{"ad": "Parol", "saatler": ["08:00","16:00","00:00"], "gun": 7, "alinan": ["08:00"]}`
Her değişiklikten sonra liste `ilaclar.csv`'ye yazılır, program açılırken oradan okunur.

Dakika mantığı: saatlerle uğraşmak zor olduğu için "SS:DD" metni **gün başından beri geçen dakikaya** çevrilir (08:30 → 8×60+30 = 510). Karşılaştırma ve toplama böylece basit sayı işlemine dönüşür.

---

## 1. Başlangıç (satır 13–22)
- `import csv` → CSV dosyası okuma/yazma. `import re` → saat biçimini (SS:DD) kontrol eden düzenli ifade. `import sys` → ekran çıktısının kodlamasını ayarlamak. `from datetime import datetime` → şimdiki saati almak.
- Sabitler (büyük harfli): dosya adları, `GUN_DAKIKA = 1440` (24×60), `YAKLASMA_ESIGI_DK = 30`. Sabit kullanmak, sayıyı kodun içine gömmekten iyidir: bir yerden değiştirirsin.

## 2. Saat dönüştürme (satır 33–58)
**`saati_dakikaya_cevir(metin)`**
1. `re.fullmatch(r"([0-9]{1,2}):([0-9]{2})", metin.strip())` → metnin *tamamı* "1-2 rakam, iki nokta, 2 rakam" biçiminde mi? `strip()` baştaki/sondaki boşluğu atar. Uymazsa `eslesme` `None` olur.
2. `None` ise `return None` (hata değil, "geçersiz" işareti; program çökmez).
3. `group(1)` saat, `group(2)` dakika; `int()` ile sayıya çevrilir.
4. `saat > 23 or dakika > 59` ise yine `None` (ör. `25:99`, `24:00`).
5. Geçerliyse `saat*60 + dakika` döner.

**`dakikayi_saate_cevir(dakika)`**: `dakika % 1440` → gece yarısını aşarsa başa sarar (1500 → 60 → "01:00"). `//60` saat, `%60` dakika; `:02d` tek haneli sayıyı "08" yapar.

**`simdiki_dakika()`**: `datetime.now()` ile şu anki saat × 60 + dakika.

## 3. Girdi alma ve doğrulama (satır 61–108)
Hepsi aynı kalıp: **`while True` içinde sor → geçerliyse `return`, değilse uyarı yaz ve döngü başa döner.** Bu yüzden hatalı girişte program çökmez, tekrar sorar.

- **`metin_oku`**: `input().strip()`; boşsa veya 40 karakterden uzunsa uyarı, değilse metni döndürür.
- **`tamsayi_oku(mesaj, alt, ust)`**: `try: int(metin)` – harf girilirse `except ValueError` yakalanır ve uyarı verilir (`continue` döngüyü başa alır). Sayı geldiyse `alt`–`ust` aralığı `if` ile kontrol edilir.
- **`saat_oku`**: `saati_dakikaya_cevir` `None` dönerse uyarı; geçerliyse `dakikayi_saate_cevir` ile "8:30" → "08:30" biçimine düzeltilip döner.
- **`evet_mi`**: `e/evet` → `True`, `h/hayır` → `False`, başka şey → uyarı ve tekrar. `.lower()` büyük/küçük harf farkını yok eder.

## 4. Doz hesaplama mantığı (satır 111–175)
**`doz_saatlerini_hesapla(ilk_saat, gunluk_doz)`**
- Geçersiz saat ya da `gunluk_doz < 1` ise `raise ValueError` (çağıran taraf hatayı bilsin).
- `aralik = 1440 // gunluk_doz` → 24 saati eşit böler (3 doz → 480 dk = 8 saat).
- `for sira in range(gunluk_doz)`: her dozun saati = `başlangıç + sıra × aralık`; `dakikayi_saate_cevir` gece yarısını sarar. 08:00, 3 doz → 480, 960, 1440→"00:00".

**`doz_dakikalari(ilac)`**: Her doz için `(saat_metni, dakika)` çifti üretir. İlk dozdan **küçük** çıkan saat ertesi güne aittir, bu yüzden `+1440` eklenir (00:00 → 1440). Böylece 08:00, 16:00, 00:00 sıralaması doğru kalır.

**`durum_belirle(doz_dakikasi, simdi_dakikasi, alindi)`** – karar yapısının kalbi:
- `alindi` ise "ALINDI".
- `fark = doz − şimdi`; `fark < 0` → "GECİKTİ"; `0 ≤ fark ≤ 30` → "YAKLAŞIYOR"; yoksa "BEKLİYOR". (`if / elif / else`)

**`gunluk_plan(ilaclar, simdi)`**: iç içe `for` – her ilaç, her ilacın her dozu. `gun <= 0` (tedavi bitti) ise `continue` ile atlanır. Her doz bir sözlük olarak `satirlar` listesine eklenir; en sonda `sort(key=lambda satir: satir["dakika"])` ile zamana göre sıralanır.

**`sonraki_doz_bul`**: sıralı planda ilk "ALINDI olmayan" satırı döndürür; hepsi alındıysa `None`.

**`fark_metni`**: `divmod(abs(fark), 60)` ile saat ve dakikayı ayırır; negatifse "gecikti", pozitifse "sonra" yazar, 0 ise "şimdi".

## 5. Ekran çıktıları (satır 190–240)
`plan_tablosu`, `ilac_tablosu`: f-string'de `{metin:<24}` → metni 24 karakterlik alanda **sola hizalar**, böylece sütunlar düzgün durur. Satırlar listede toplanıp `"\n".join(...)` ile tek metne birleştirilir.
`hatirlatma_metni`: sonraki dozu bulur, yoksa "bekleyen doz yok" der.
`rapor_metni`: planı, alınan/geciken sayılarını (`sum(1 for ...)` = koşulu sağlayanları say) ve hatırlatmayı tek metinde birleştirir. Metin döndürür, **yazmaz** – yazma işi ayrı fonksiyonda (test etmek kolay olsun diye).

## 6. Dosya işlemleri (satır 243–293)
- **`dosyaya_kaydet`**: `with open(..., "w", newline="", encoding="utf-8-sig")` → dosya işi bitince otomatik kapanır. `csv.writer` her ilaç için bir satır yazar; saat listesi `"|".join(...)` ile tek hücreye sıkıştırılır. `except OSError` → disk/izin hatasında çökmez, uyarı verir.
- **`dosyadan_yukle`**: `csv.DictReader` sütun adlarıyla okur. Her satır için `split("|")` listeyi geri kurar, saatler doğrulanır. Bozuk satır (`ValueError`, `KeyError`...) uyarıyla **atlanır**. `FileNotFoundError` ilk çalıştırmada normaldir → boş liste döner.
- **`raporu_kaydet`**: metni `.txt`'ye yazar.

## 7. Menü işlemleri (satır 296–378)
- **`ilac_ekle`**: 4 girdi alır (ad, ilk saat, günlük doz 1–12, gün 1–365). Önce aynı isim var mı bakar (`lower()` ile büyük/küçük harfi yok sayarak). Sonra `doz_saatlerini_hesapla` ile saatleri üretip sözlüğü listeye `append` eder. Eklendiyse `True`, eklenmediyse `False` döner – `main` buna bakıp kaydeder.
- **`ilac_sec`**: tabloyu gösterip numara ister, `-1` ile liste sırasına (0'dan başlar) çevirir.
- **`doz_isaretle`**: boş listeyi kontrol eder; seçilen ilacın **henüz alınmamış** saatlerini (liste üreteci `[s for s in ... if s not in ...]`) numaralı gösterir; seçileni `alinan` listesine ekler.
- **`ilac_sil`**: `evet_mi` ile onay ister; `pop(sira)` listeden çıkarır.
- **`yeni_gune_gec`**: onay sonrası her ilaç için `gun -= 1`, `alinan = []`; gün 0 olursa "tedavi tamamlandı" yazar.

## 8. `main()` (satır 381–427)
1. `sys.stdout.reconfigure(encoding="utf-8")` → Windows'ta Türkçe karakter bozulmasın (olmazsa `except` ile geçilir).
2. `dosyadan_yukle()` → önceki ilaçlar gelir.
3. `while True`: menü yazılır, `secim = input().strip()`.
4. `if / elif` zinciri seçimi işleme bağlar: "1" ekle, "2" listele, "3" plan, "4" işaretle, "5" sil, "6" rapor, "7" yeni gün, "0" kaydet ve `break` (döngüden çık). Başka her şey `else` ile "geçersiz seçim" uyarısı verir (örn. `9` ya da boş).
5. Veriyi değiştiren işlemler `True` dönerse `dosyaya_kaydet` çağrılır.

## 9. Dosyanın sonu (satır 430–)
`if __name__ == "__main__":` → dosya doğrudan çalıştırılınca `main()` başlar; **testler `import` ettiğinde başlamaz**. `try/except (KeyboardInterrupt, EOFError)` → Ctrl+C ya da girdi bitişinde çirkin hata yerine "Program kapatıldı." yazar.

---

## Sözlü doğrulamada sorulabilecek sorular (kısa cevaplarla)
1. **Neden saatleri dakikaya çeviriyorsun?** Sayıyla karşılaştırma/toplama kolay; "08:00 < 16:00" gibi metin karşılaştırması gece yarısında yanlış olur.
2. **`%` (mod) neden kullanıldı?** 1440'ı geçen dakikayı 24 saatlik saate geri sarmak için (1500 % 1440 = 60 → 01:00).
3. **`while True` içinde `return` nasıl çıkış sağlıyor?** Geçerli değer bulununca fonksiyon biter, döngü de biter.
4. **Hatalı girişte neden çökmüyor?** `int()` hatasını `try/except ValueError` yakalıyor; saat için regex + aralık kontrolü `None` döndürüyor; her şey tekrar sorma döngüsü içinde.
5. **Neden liste of sözlük?** Her ilacın birden fazla alanı var (ad, saatler, gün, alınanlar); sözlük alanları isimle tutar, liste ilaçları sıralı saklar.
6. **`fonksiyon` neden ekrana yazmak yerine metin döndürüyor (`rapor_metni`)?** Hem ekrana hem dosyaya aynı metin gidebilir; test etmesi kolay.
7. **Bilinen sınırlama nedir?** Plan, ilk dozdan başlayan 24 saatlik döngü; 22:00'de başlayan ilacın 10:00 dozu ertesi güne sayılır.
