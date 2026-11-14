"""İlaç / Tedavi Saatleri Hatırlatıcı Planlayıcı (komut satırı uygulaması).

GEP1316 Kodlama Okuryazarlığı - Ara Değerlendirme Ödevi 1.

Kullanıcı ilaçlarını (ad, ilk doz saati, günlük doz sayısı, tedavi süresi)
girer. Program doz saatlerini 24 saate eşit bölerek hesaplar, bugünün planını
gösterir, geciken / yaklaşan dozları hatırlatır ve sonuçları dosyalara kaydeder.

UYARI: Bu program tıbbi tavsiye vermez; yalnızca kullanıcının girdiği saatleri
düzenler. Kişisel sağlık verisi girmeyiniz.
"""

import csv
import re
import sys
from datetime import datetime

# ---------------------------------------------------------------- sabitler
CSV_DOSYASI = "ilaclar.csv"          # kalıcı veri (ilaç listesi)
RAPOR_DOSYASI = "gunluk_plan.txt"    # insan okuyabilir günlük rapor
GUN_DAKIKA = 24 * 60                 # bir gündeki dakika sayısı (1440)
YAKLASMA_ESIGI_DK = 30               # "yaklaşıyor" uyarısı için eşik (dakika)

# Bir ilaç, sözlük olarak tutulur; tüm ilaçlar bir listededir:
# {"ad": "Aspirin", "saatler": ["08:00", "16:00"], "gun": 7, "alinan": ["08:00"]}
#   ad      -> ilaç adı
#   saatler -> günlük doz saatleri ("SS:DD"), ilki başlangıç saatidir
#   gun     -> kalan tedavi günü sayısı
#   alinan  -> bugün alındı olarak işaretlenen saatler


# ------------------------------------------------- saat dönüştürme yardımcıları
def saati_dakikaya_cevir(metin):
    """'SS:DD' metnini gün başından itibaren dakikaya çevirir (0-1439).

    Biçim ya da aralık hatalıysa None döndürür (program çökmez).
    """
    eslesme = re.fullmatch(r"([0-9]{1,2}):([0-9]{2})", metin.strip())
    if eslesme is None:
        return None
    saat = int(eslesme.group(1))
    dakika = int(eslesme.group(2))
    if saat > 23 or dakika > 59:
        return None
    return saat * 60 + dakika


def dakikayi_saate_cevir(dakika):
    """Dakika sayısını 'SS:DD' metnine çevirir (gece yarısını aşarsa başa sarar)."""
    dakika = dakika % GUN_DAKIKA
    return f"{dakika // 60:02d}:{dakika % 60:02d}"


def simdiki_dakika():
    """Şu anki saati gün başından itibaren dakika olarak verir."""
    simdi = datetime.now()
    return simdi.hour * 60 + simdi.minute


# ---------------------------------------------------- girdi alma ve doğrulama
def metin_oku(mesaj, en_uzun=40):
    """Boş olmayan, makul uzunlukta bir metin ister; hatalıysa tekrar sorar."""
    while True:
        metin = input(mesaj).strip()
        if metin == "":
            print("  ! Uyarı: Bu alan boş bırakılamaz.")
        elif len(metin) > en_uzun:
            print(f"  ! Uyarı: En fazla {en_uzun} karakter girebilirsiniz.")
        else:
            return metin


def tamsayi_oku(mesaj, alt, ust):
    """alt ile ust (dahil) arasında bir tam sayı ister; hatalıysa tekrar sorar."""
    while True:
        metin = input(mesaj).strip()
        try:
            sayi = int(metin)
        except ValueError:
            print("  ! Uyarı: Lütfen sayı giriniz (örnek: 3).")
            continue
        if sayi < alt or sayi > ust:
            print(f"  ! Uyarı: Sayı {alt} ile {ust} arasında olmalıdır.")
        else:
            return sayi


def saat_oku(mesaj):
    """'SS:DD' biçiminde geçerli bir saat ister; 'SS:DD' metni döndürür."""
    while True:
        dakika = saati_dakikaya_cevir(input(mesaj))
        if dakika is None:
            print("  ! Uyarı: Saat 'SS:DD' biçiminde olmalı (örnek: 08:30, 00:00-23:59).")
        else:
            return dakikayi_saate_cevir(dakika)


def evet_mi(mesaj):
    """e/h sorusu sorar; 'e' ise True, 'h' ise False döndürür."""
    while True:
        cevap = input(mesaj + " (e/h): ").strip().lower()
        if cevap in ("e", "evet"):
            return True
        elif cevap in ("h", "hayır", "hayir"):
            return False
        else:
            print("  ! Uyarı: Lütfen 'e' veya 'h' yazınız.")


# ------------------------------------------------------- doz hesaplama mantığı
def doz_saatlerini_hesapla(ilk_saat, gunluk_doz):
    """İlk doz saatinden başlayarak 24 saati eşit bölüp doz saatlerini döndürür.

    Örnek: ("08:00", 3) -> ["08:00", "16:00", "00:00"]
    """
    baslangic = saati_dakikaya_cevir(ilk_saat)
    if baslangic is None or gunluk_doz < 1:
        raise ValueError("Geçersiz ilk saat ya da günlük doz sayısı")
    aralik = GUN_DAKIKA // gunluk_doz
    saatler = []
    for sira in range(gunluk_doz):
        saatler.append(dakikayi_saate_cevir(baslangic + sira * aralik))
    return saatler


def doz_dakikalari(ilac):
    """İlacın dozlarını (saat_metni, dakika) çiftleri olarak döndürür.

    Plan, ilk dozdan başlayan 24 saatlik bir döngüdür. İlk dozdan 'önce'
    görünen saatler (ör. 08:00 başlangıçlı planda 00:00) ertesi güne aittir,
    bu yüzden 1440 dakika eklenir.
    """
    ilk = saati_dakikaya_cevir(ilac["saatler"][0])
    sonuc = []
    for saat in ilac["saatler"]:
        dakika = saati_dakikaya_cevir(saat)
        if dakika < ilk:
            dakika += GUN_DAKIKA
        sonuc.append((saat, dakika))
    return sonuc


def durum_belirle(doz_dakikasi, simdi_dakikasi, alindi):
    """Dozun durumunu belirler: ALINDI / GECİKTİ / YAKLAŞIYOR / BEKLİYOR."""
    if alindi:
        return "ALINDI"
    fark = doz_dakikasi - simdi_dakikasi
    if fark < 0:
        return "GECİKTİ"
    elif fark <= YAKLASMA_ESIGI_DK:
        return "YAKLAŞIYOR"
    else:
        return "BEKLİYOR"


def gunluk_plan(ilaclar, simdi_dakikasi):
    """Tedavisi süren tüm ilaçların bugünkü dozlarını zamana göre sıralı verir."""
    satirlar = []
    for ilac in ilaclar:
        if ilac["gun"] <= 0:          # tedavi bitmiş ilaçlar plana girmez
            continue
        for saat, dakika in doz_dakikalari(ilac):
            durum = durum_belirle(dakika, simdi_dakikasi, saat in ilac["alinan"])
            satirlar.append({"ad": ilac["ad"], "saat": saat,
                             "dakika": dakika, "durum": durum})
    satirlar.sort(key=lambda satir: satir["dakika"])
    return satirlar


def sonraki_doz_bul(ilaclar, simdi_dakikasi):
    """Henüz alınmamış en erken dozu döndürür; hepsi alındıysa None."""
    for satir in gunluk_plan(ilaclar, simdi_dakikasi):
        if satir["durum"] != "ALINDI":
            return satir
    return None


def fark_metni(fark_dakika):
    """Dakika farkını 'X sa Y dk sonra / gecikti' biçiminde yazıya döker."""
    if fark_dakika == 0:
        return "şimdi"
    saat, dakika = divmod(abs(fark_dakika), 60)
    parca = f"{saat} sa {dakika} dk" if saat > 0 else f"{dakika} dk"
    if fark_dakika < 0:
        return f"{parca} gecikti"
    return f"{parca} sonra"


# ------------------------------------------------------------ ekran çıktıları
def plan_tablosu(satirlar):
    """Plan satırlarını hizalı bir tablo metni olarak döndürür."""
    if not satirlar:
        return "  (Planlanmış doz yok.)"
    satirlar_metin = [f"  {'SAAT':<7}{'İLAÇ':<24}{'DURUM'}", "  " + "-" * 45]
    for satir in satirlar:
        satirlar_metin.append(
            f"  {satir['saat']:<7}{satir['ad']:<24}{satir['durum']}")
    return "\n".join(satirlar_metin)


def ilac_tablosu(ilaclar):
    """İlaç listesini hizalı bir tablo metni olarak döndürür."""
    if not ilaclar:
        return "  (Kayıtlı ilaç yok.)"
    metin = [f"  {'NO':<4}{'İLAÇ':<22}{'DOZ SAATLERİ':<28}{'KALAN GÜN':<11}{'ALINAN'}",
             "  " + "-" * 72]
    for no, ilac in enumerate(ilaclar, start=1):
        saatler = ", ".join(ilac["saatler"])
        alinan = f"{len(ilac['alinan'])}/{len(ilac['saatler'])}"
        gun = str(ilac["gun"]) if ilac["gun"] > 0 else "bitti"
        metin.append(f"  {no:<4}{ilac['ad']:<22}{saatler:<28}{gun:<11}{alinan}")
    return "\n".join(metin)


def hatirlatma_metni(ilaclar, simdi_dakikasi):
    """Sonraki dozla ilgili tek satırlık hatırlatma metni üretir."""
    satir = sonraki_doz_bul(ilaclar, simdi_dakikasi)
    if satir is None:
        return "Bugün için bekleyen doz yok."
    fark = satir["dakika"] - simdi_dakikasi
    return f"Sonraki doz: {satir['ad']} saat {satir['saat']} ({fark_metni(fark)})"


def rapor_metni(ilaclar, simdi_dakikasi, tarih_metni):
    """Dosyaya yazılacak günlük raporun tamamını metin olarak döndürür."""
    satirlar = gunluk_plan(ilaclar, simdi_dakikasi)
    alinan = sum(1 for satir in satirlar if satir["durum"] == "ALINDI")
    geciken = sum(1 for satir in satirlar if satir["durum"] == "GECİKTİ")
    parcalar = [
        "İLAÇ HATIRLATICI - GÜNLÜK PLAN RAPORU",
        f"Tarih / saat : {tarih_metni}",
        "=" * 47,
        plan_tablosu(satirlar),
        "=" * 47,
        f"Toplam doz: {len(satirlar)} | Alınan: {alinan} | Geciken: {geciken}",
        hatirlatma_metni(ilaclar, simdi_dakikasi),
        "Not: Bu rapor tıbbi tavsiye değildir.",
    ]
    return "\n".join(parcalar) + "\n"


# --------------------------------------------------------- dosya okuma / yazma
def dosyaya_kaydet(ilaclar, yol=CSV_DOSYASI):
    """İlaç listesini CSV dosyasına yazar. Başarılıysa True döner."""
    try:
        with open(yol, "w", newline="", encoding="utf-8-sig") as dosya:
            yazici = csv.writer(dosya)
            yazici.writerow(["ad", "saatler", "gun", "alinan"])
            for ilac in ilaclar:
                yazici.writerow([ilac["ad"], "|".join(ilac["saatler"]),
                                 ilac["gun"], "|".join(ilac["alinan"])])
        return True
    except OSError as hata:
        print(f"  ! Uyarı: Dosya kaydedilemedi ({hata}).")
        return False


def dosyadan_yukle(yol=CSV_DOSYASI):
    """CSV dosyasından ilaç listesini okur; dosya yoksa boş liste döndürür.

    Bozuk satırlar atlanır, program çökmez.
    """
    ilaclar = []
    try:
        with open(yol, newline="", encoding="utf-8-sig") as dosya:
            for satir in csv.DictReader(dosya):
                try:
                    saatler = satir["saatler"].split("|")
                    for saat in saatler:
                        if saati_dakikaya_cevir(saat) is None:
                            raise ValueError("bozuk saat")
                    alinan = [s for s in satir["alinan"].split("|") if s in saatler]
                    ilaclar.append({"ad": satir["ad"], "saatler": saatler,
                                    "gun": int(satir["gun"]), "alinan": alinan})
                except (ValueError, KeyError, AttributeError, TypeError):
                    print("  ! Uyarı: Dosyadaki bozuk bir satır atlandı.")
    except FileNotFoundError:
        pass                                  # ilk çalıştırma: dosya henüz yok
    except OSError as hata:
        print(f"  ! Uyarı: Dosya okunamadı ({hata}).")
    return ilaclar


def raporu_kaydet(metin, yol=RAPOR_DOSYASI):
    """Rapor metnini .txt dosyasına yazar. Başarılıysa True döner."""
    try:
        with open(yol, "w", encoding="utf-8") as dosya:
            dosya.write(metin)
        return True
    except OSError as hata:
        print(f"  ! Uyarı: Rapor kaydedilemedi ({hata}).")
        return False


# ---------------------------------------------------------- menü işlemleri
def ilac_ekle(ilaclar):
    """Kullanıcıdan 4 bilgi alıp yeni bir ilaç ekler."""
    print("\n--- Yeni İlaç Ekle ---")
    ad = metin_oku("İlaç adı: ")
    for ilac in ilaclar:
        if ilac["ad"].lower() == ad.lower():
            print("  ! Uyarı: Bu isimde bir ilaç zaten kayıtlı.")
            return False
    ilk_saat = saat_oku("İlk doz saati (SS:DD): ")
    gunluk_doz = tamsayi_oku("Günde kaç doz (1-12): ", 1, 12)
    gun = tamsayi_oku("Tedavi kaç gün sürecek (1-365): ", 1, 365)
    saatler = doz_saatlerini_hesapla(ilk_saat, gunluk_doz)
    ilaclar.append({"ad": ad, "saatler": saatler, "gun": gun, "alinan": []})
    print(f"  Eklendi: {ad} -> doz saatleri: {', '.join(saatler)}")
    return True


def ilac_sec(ilaclar, mesaj):
    """Listeden bir ilaç seçtirir; seçilen ilacın sırasını (0'dan) döndürür."""
    print(ilac_tablosu(ilaclar))
    return tamsayi_oku(mesaj, 1, len(ilaclar)) - 1


def doz_isaretle(ilaclar):
    """Seçilen ilacın bekleyen bir dozunu 'alındı' olarak işaretler."""
    if not ilaclar:
        print("  ! Önce ilaç eklemelisiniz.")
        return False
    ilac = ilaclar[ilac_sec(ilaclar, "Hangi ilaç (no): ")]
    bekleyenler = [s for s in ilac["saatler"] if s not in ilac["alinan"]]
    if not bekleyenler:
        print("  Bu ilacın bugünkü tüm dozları zaten alındı.")
        return False
    for no, saat in enumerate(bekleyenler, start=1):
        print(f"  {no}) {saat}")
    secim = tamsayi_oku("Hangi doz alındı (no): ", 1, len(bekleyenler))
    ilac["alinan"].append(bekleyenler[secim - 1])
    print(f"  İşaretlendi: {ilac['ad']} {bekleyenler[secim - 1]} alındı.")
    return True


def ilac_sil(ilaclar):
    """Seçilen ilacı onay aldıktan sonra listeden siler."""
    if not ilaclar:
        print("  ! Silinecek ilaç yok.")
        return False
    sira = ilac_sec(ilaclar, "Silinecek ilaç (no): ")
    if evet_mi(f"'{ilaclar[sira]['ad']}' silinsin mi?"):
        silinen = ilaclar.pop(sira)
        print(f"  Silindi: {silinen['ad']}")
        return True
    print("  Silme iptal edildi.")
    return False


def yeni_gune_gec(ilaclar):
    """Alınan dozları sıfırlar ve her ilacın kalan tedavi gününü 1 azaltır."""
    if not ilaclar:
        print("  ! Kayıtlı ilaç yok.")
        return False
    if not evet_mi("Yeni güne geçilsin mi (alınan dozlar sıfırlanır)?"):
        return False
    for ilac in ilaclar:
        if ilac["gun"] > 0:
            ilac["gun"] -= 1
            ilac["alinan"] = []
            if ilac["gun"] == 0:
                print(f"  Tedavi tamamlandı: {ilac['ad']}")
    print("  Yeni gün başladı.")
    return True


def menuyu_goster():
    """Ana menüyü ekrana yazar."""
    print("\n===== İLAÇ HATIRLATICI =====")
    print("1) İlaç ekle")
    print("2) İlaçları listele")
    print("3) Bugünün planı ve hatırlatma")
    print("4) Doz alındı olarak işaretle")
    print("5) İlaç sil")
    print("6) Raporu dosyaya kaydet")
    print("7) Yeni güne geç")
    print("0) Çıkış")


def main():
    """Programın ana döngüsü: menüyü gösterir, seçime göre işlem yapar."""
    # Windows'ta Türkçe karakterlerin düzgün yazılması için (hata olursa geç)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    print("Uyarı: Bu program tıbbi tavsiye vermez. Kişisel sağlık verisi girmeyiniz.")
    ilaclar = dosyadan_yukle()
    if ilaclar:
        print(f"{len(ilaclar)} kayıtlı ilaç yüklendi.")

    while True:
        menuyu_goster()
        secim = input("Seçiminiz: ").strip()
        if secim == "1":
            if ilac_ekle(ilaclar):
                dosyaya_kaydet(ilaclar)
        elif secim == "2":
            print(ilac_tablosu(ilaclar))
        elif secim == "3":
            simdi = simdiki_dakika()
            print(f"\nŞu an: {dakikayi_saate_cevir(simdi)}")
            print(plan_tablosu(gunluk_plan(ilaclar, simdi)))
            print(hatirlatma_metni(ilaclar, simdi))
        elif secim == "4":
            if doz_isaretle(ilaclar):
                dosyaya_kaydet(ilaclar)
        elif secim == "5":
            if ilac_sil(ilaclar):
                dosyaya_kaydet(ilaclar)
        elif secim == "6":
            simdi = datetime.now()
            metin = rapor_metni(ilaclar, simdiki_dakika(),
                                simdi.strftime("%d.%m.%Y %H:%M"))
            if raporu_kaydet(metin):
                print(f"  Rapor kaydedildi: {RAPOR_DOSYASI}")
        elif secim == "7":
            if yeni_gune_gec(ilaclar):
                dosyaya_kaydet(ilaclar)
        elif secim == "0":
            dosyaya_kaydet(ilaclar)
            print("Görüşmek üzere, sağlıklı günler!")
            break
        else:
            print("  ! Uyarı: Geçersiz seçim. Menüden 0-7 arası bir sayı giriniz.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram kapatıldı.")
