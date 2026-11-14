"""ilac_hatirlatici.py için otomatik testler.

Çalıştırma:  python -m unittest -v
Girdi (input) fonksiyonu sahte değerlerle değiştirilir; testler gerçek saate
ya da klavyeye bağlı değildir.
"""

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import ilac_hatirlatici as ih


def sessiz_calistir(islev, *argumanlar, girdiler=()):
    """İşlevi sahte klavye girdileriyle çalıştırır; ekran çıktısını yakalar.

    (islev sonucu, ekrana yazılan metin) çifti döndürür.
    """
    cikti = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(girdiler)):
        with contextlib.redirect_stdout(cikti):
            sonuc = islev(*argumanlar)
    return sonuc, cikti.getvalue()


def ornek_ilac(ad="Aspirin", saatler=("08:00", "16:00", "00:00"), gun=5, alinan=()):
    return {"ad": ad, "saatler": list(saatler), "gun": gun, "alinan": list(alinan)}


class SaatDogrulamaTesti(unittest.TestCase):
    """Test 1-4: saat biçimi doğrulama (geçerli, hatalı ve sınır değerler)."""

    def test_gecerli_saat(self):
        self.assertEqual(ih.saati_dakikaya_cevir("08:00"), 480)
        self.assertEqual(ih.saati_dakikaya_cevir(" 8:30 "), 510)

    def test_hatali_saat_degeri(self):
        self.assertIsNone(ih.saati_dakikaya_cevir("25:99"))
        self.assertIsNone(ih.saati_dakikaya_cevir("12:60"))

    def test_hatali_saat_bicimi(self):
        for metin in ("abc", "", "8", "08.00", "08:5", "-1:30"):
            with self.subTest(metin=metin):
                self.assertIsNone(ih.saati_dakikaya_cevir(metin))

    def test_sinir_saatleri(self):
        self.assertEqual(ih.saati_dakikaya_cevir("00:00"), 0)
        self.assertEqual(ih.saati_dakikaya_cevir("23:59"), 1439)
        self.assertIsNone(ih.saati_dakikaya_cevir("24:00"))


class GirdiOkumaTesti(unittest.TestCase):
    """Test 5-8: hatalı girdide program çökmez, tekrar sorar."""

    def test_bos_ilac_adi_tekrar_sorulur(self):
        sonuc, cikti = sessiz_calistir(ih.metin_oku, "Ad: ",
                                       girdiler=["", "   ", "Aspirin"])
        self.assertEqual(sonuc, "Aspirin")
        self.assertEqual(cikti.count("Uyarı"), 2)

    def test_cok_uzun_ad_reddedilir(self):
        sonuc, _ = sessiz_calistir(ih.metin_oku, "Ad: ",
                                   girdiler=["x" * 41, "Parol"])
        self.assertEqual(sonuc, "Parol")

    def test_tamsayi_hatali_ve_aralik_disi(self):
        sonuc, cikti = sessiz_calistir(ih.tamsayi_oku, "Doz: ", 1, 12,
                                       girdiler=["0", "-3", "abc", "13", "3"])
        self.assertEqual(sonuc, 3)
        self.assertEqual(cikti.count("Uyarı"), 4)

    def test_saat_oku_hatali_sonra_gecerli(self):
        sonuc, _ = sessiz_calistir(ih.saat_oku, "Saat: ",
                                   girdiler=["25:99", "abc", "8:30"])
        self.assertEqual(sonuc, "08:30")

    def test_evet_hayir(self):
        sonuc, _ = sessiz_calistir(ih.evet_mi, "Emin misiniz?",
                                   girdiler=["belki", "E"])
        self.assertTrue(sonuc)
        sonuc, _ = sessiz_calistir(ih.evet_mi, "Emin misiniz?", girdiler=["h"])
        self.assertFalse(sonuc)


class DozHesaplamaTesti(unittest.TestCase):
    """Test 9-12: doz saatlerinin hesaplanması ve gece yarısı geçişi."""

    def test_uc_doz(self):
        self.assertEqual(ih.doz_saatlerini_hesapla("08:00", 3),
                         ["08:00", "16:00", "00:00"])

    def test_tek_doz(self):
        self.assertEqual(ih.doz_saatlerini_hesapla("21:15", 1), ["21:15"])

    def test_gece_yarisi_sarma(self):
        self.assertEqual(ih.doz_saatlerini_hesapla("22:00", 2), ["22:00", "10:00"])

    def test_gecersiz_arguman_hata_verir(self):
        with self.assertRaises(ValueError):
            ih.doz_saatlerini_hesapla("08:00", 0)
        with self.assertRaises(ValueError):
            ih.doz_saatlerini_hesapla("99:00", 2)


class DurumVePlanTesti(unittest.TestCase):
    """Test 13-18: doz durumu, sıralama, hatırlatma, biten tedavi."""

    def test_durumlar(self):
        self.assertEqual(ih.durum_belirle(480, 600, True), "ALINDI")
        self.assertEqual(ih.durum_belirle(480, 600, False), "GECİKTİ")
        self.assertEqual(ih.durum_belirle(630, 600, False), "YAKLAŞIYOR")   # tam 30 dk
        self.assertEqual(ih.durum_belirle(631, 600, False), "BEKLİYOR")     # 31 dk

    def test_gece_yarisi_dozu_ertesi_gune_sayilir(self):
        ilac = ornek_ilac()                    # 08:00, 16:00, 00:00
        dakikalar = [dk for _, dk in ih.doz_dakikalari(ilac)]
        self.assertEqual(dakikalar, [480, 960, 1440])

    def test_gece_yarisi_oncesi_yaklasan_doz(self):
        ilac = ornek_ilac(alinan=["08:00", "16:00"])
        simdi = ih.saati_dakikaya_cevir("23:30")
        satir = ih.sonraki_doz_bul([ilac], simdi)
        self.assertEqual(satir["saat"], "00:00")
        self.assertEqual(satir["durum"], "YAKLAŞIYOR")
        self.assertEqual(ih.fark_metni(satir["dakika"] - simdi), "30 dk sonra")

    def test_plan_zamana_gore_siralanir(self):
        ilaclar = [ornek_ilac("B", ("20:00",)), ornek_ilac("A", ("07:00", "19:00"))]
        saatler = [s["saat"] for s in ih.gunluk_plan(ilaclar, 0)]
        self.assertEqual(saatler, ["07:00", "19:00", "20:00"])

    def test_biten_tedavi_plana_girmez(self):
        ilaclar = [ornek_ilac("Eski", gun=0), ornek_ilac("Yeni", ("09:00",), gun=2)]
        plan = ih.gunluk_plan(ilaclar, 0)
        self.assertEqual([s["ad"] for s in plan], ["Yeni"])

    def test_tum_dozlar_alindiysa_sonraki_yok(self):
        ilac = ornek_ilac(alinan=["08:00", "16:00", "00:00"])
        self.assertIsNone(ih.sonraki_doz_bul([ilac], 0))
        self.assertEqual(ih.hatirlatma_metni([ilac], 0),
                         "Bugün için bekleyen doz yok.")


class MenuIslemleriTesti(unittest.TestCase):
    """Test 19-23: ilaç ekleme, işaretleme, silme, yeni gün."""

    def test_ilac_ekle(self):
        ilaclar = []
        sonuc, _ = sessiz_calistir(ih.ilac_ekle, ilaclar,
                                   girdiler=["Parol", "09:00", "2", "7"])
        self.assertTrue(sonuc)
        self.assertEqual(ilaclar[0], {"ad": "Parol", "saatler": ["09:00", "21:00"],
                                      "gun": 7, "alinan": []})

    def test_ayni_isimli_ilac_eklenmez(self):
        ilaclar = [ornek_ilac("Parol")]
        sonuc, cikti = sessiz_calistir(ih.ilac_ekle, ilaclar, girdiler=["parol"])
        self.assertFalse(sonuc)
        self.assertEqual(len(ilaclar), 1)
        self.assertIn("zaten kayıtlı", cikti)

    def test_doz_isaretle(self):
        ilaclar = [ornek_ilac()]
        sonuc, _ = sessiz_calistir(ih.doz_isaretle, ilaclar, girdiler=["1", "2"])
        self.assertTrue(sonuc)
        self.assertEqual(ilaclar[0]["alinan"], ["16:00"])

    def test_bos_listede_isaretleme_ve_silme_cokmez(self):
        self.assertFalse(sessiz_calistir(ih.doz_isaretle, [])[0])
        self.assertFalse(sessiz_calistir(ih.ilac_sil, [])[0])

    def test_silme_onayi(self):
        ilaclar = [ornek_ilac()]
        sonuc, _ = sessiz_calistir(ih.ilac_sil, ilaclar, girdiler=["1", "h"])
        self.assertFalse(sonuc)
        self.assertEqual(len(ilaclar), 1)
        sonuc, _ = sessiz_calistir(ih.ilac_sil, ilaclar, girdiler=["1", "e"])
        self.assertTrue(sonuc)
        self.assertEqual(ilaclar, [])

    def test_yeni_gune_gec(self):
        ilaclar = [ornek_ilac(gun=2, alinan=["08:00"]),
                   ornek_ilac("Biten", ("10:00",), gun=1)]
        sessiz_calistir(ih.yeni_gune_gec, ilaclar, girdiler=["e"])
        self.assertEqual(ilaclar[0]["gun"], 1)
        self.assertEqual(ilaclar[0]["alinan"], [])
        self.assertEqual(ilaclar[1]["gun"], 0)


class DosyaTesti(unittest.TestCase):
    """Test 24-27: CSV ve rapor dosyası."""

    def setUp(self):
        self.klasor = tempfile.TemporaryDirectory()
        self.addCleanup(self.klasor.cleanup)

    def yol(self, ad):
        return os.path.join(self.klasor.name, ad)

    def test_csv_kaydet_ve_yukle(self):
        ilaclar = [ornek_ilac("Vitamin C", ("08:00", "20:00"), 10, ["08:00"])]
        self.assertTrue(ih.dosyaya_kaydet(ilaclar, self.yol("a.csv")))
        self.assertEqual(ih.dosyadan_yukle(self.yol("a.csv")), ilaclar)

    def test_dosya_yoksa_bos_liste(self):
        self.assertEqual(ih.dosyadan_yukle(self.yol("yok.csv")), [])

    def test_bozuk_satir_atlanir(self):
        with open(self.yol("b.csv"), "w", encoding="utf-8") as dosya:
            dosya.write("ad,saatler,gun,alinan\n"
                        "Iyi,08:00|20:00,3,\n"
                        "Kotu,99:99,3,\n"
                        "Kotu2,08:00,abc,\n")
        ilaclar, cikti = sessiz_calistir(ih.dosyadan_yukle, self.yol("b.csv"))
        self.assertEqual([i["ad"] for i in ilaclar], ["Iyi"])
        self.assertEqual(cikti.count("bozuk"), 2)

    def test_rapor_icerigi_ve_kayit(self):
        ilaclar = [ornek_ilac(alinan=["08:00"])]
        metin = ih.rapor_metni(ilaclar, ih.saati_dakikaya_cevir("10:00"),
                               "14.11.2026 10:00")
        self.assertIn("Toplam doz: 3 | Alınan: 1 | Geciken: 0", metin)
        self.assertTrue(ih.raporu_kaydet(metin, self.yol("r.txt")))
        with open(self.yol("r.txt"), encoding="utf-8") as dosya:
            self.assertEqual(dosya.read(), metin)


if __name__ == "__main__":
    unittest.main()
