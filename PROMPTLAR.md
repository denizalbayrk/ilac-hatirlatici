# PROMPTLAR – YZ ile Çalışma Günlüğü

**Araç:** Claude Code (Claude Sonnet 5.5, Anthropic) – masaüstü uygulaması, bu proje klasöründe.
**Not:** Aşağıya kişisel veri girilmemiştir. Her kayıt: prompt → YZ'nin yaptığı → benim kararım ve gerekçem.

---

## Prompt 1 – Ödevi anlatma ve ilk istek
**Prompt (özet):** Ödev açıklamasının ekran görüntülerini (amaç, senaryo, gereksinimler, rubrik, teslim kuralları) verdim. Konumun "ilaç/tedavi saatleri hatırlatıcı planlayıcı" olduğunu, ödevi amaç ve gereksinimlere uygun olarak önce yerelde tamamlamasını, GitHub hesabını sonradan bağlayıp commit/push yapacağımı yazdım.

**YZ yanıtı:** Önce kod yazmadan bir plan çıkardı: dosya yapısı (kod, test, README, PROMPTLAR, RAPOR), fonksiyon listesi, her gereksinimin hangi kodla karşılanacağı, test senaryoları ve dürüstlük notları (yansıtma ve beyan formunu benim doldurmam gerektiği).

**Kararım: KABUL (küçük ekle­meyle).** Plan, ödevin 8 gereksinimini tek tek eşliyordu. Planda "yeni güne geç" menüsü yoktu; kalan tedavi günü ve "tedavi bitti mi" kararı için gerekli olduğundan uygulama sırasında eklendi.

## Prompt 2 – Planın onaylanması
**Prompt (özet):** Planı onayladım; uygulamaya geçmesini istedim.

**YZ yanıtı:** `ilac_hatirlatici.py` (27 fonksiyon), `test_ilac_hatirlatici.py` (29 test), README, PROMPTLAR, RAPOR ve `.gitignore` dosyalarını yazdı; testleri ve uygulamayı hatalı girdilerle çalıştırdı.

**Kararım: KABUL, DOĞRULAMA SONRASI.** Kodu körü körüne kabul etmedim: `python -m unittest -v` ile 29 testin geçtiğini ve uygulamanın hatalı girdilerde (`25:99`, `abc`, boş, `0`, `-2`) çökmediğini gördüm.

## YZ çıktısında fark edilen eksik (düzenleme/kabul kararı)
- **Bulgu:** 22:00'de başlayıp günde 2 doz alan ilacın ikinci dozu "10:00" olarak ertesi güne sayılıyor. Öğlen 12:30'da planı açınca 10:00 dozu "BEKLİYOR" görünüyor, "GECİKTİ" değil. Çünkü plan "ilk dozdan başlayan 24 saatlik döngü" olarak tasarlanmış.
- **Karar: KABUL + belgeleme.** Tasarım basit ve açıklanabilir kalsın diye davranışı değiştirmedim; README'de "Bilinen sınırlama" olarak yazıldı. İsteğe bağlı iyileştirme: dozları takvim gününe bağlamak.

---

## Prompt 3 – Kodu satır satır açıklatma (sözlü doğrulama hazırlığı)
**Prompt (özet):** Ödevde kodu açıklayabilmem gerektiği için, YZ'den kodu satır satır açıklamasını istedim.

**YZ yanıtı:** [KOD_REHBERI.md](KOD_REHBERI.md) dosyasını yazdı: her fonksiyonun ne yaptığı, satır satır akışı, dakika/mod mantığı, hata yakalama (`try/except`), `main` döngüsü ve sözlüde sorulabilecek 7 soru.

**Kararım: KABUL, kendi okumamla doğrulayarak.** Açıklamayı kodla karşılaştırarak okudum; amacım her satırı kendi cümlelerimle anlatabilmek. Anlamadığım bir yer olursa YZ'ye yeniden sorup bu günlüğe ekleyeceğim.

## Prompt 4 – GitHub'a gönderme
**Prompt (özet):** GitHub kullanıcı adımı, e-postamı ve şifremi yazıp gerekli işlemleri yapmasını istedim.

**YZ yanıtı:** Şifreyi hiçbir yere girmedi (kimlik doğrulamayı benim yapmam gerektiğini söyledi). Git kimliğini (kullanıcı adı, e-posta) yalnızca bu depoya özel ayarladı ve yerel ilk commit'i attı. Bilgisayardaki GitHub oturumunun başka bir hesapta açık olduğunu fark edip push etmeden durdu; `gh auth login` ile kendi hesabıma girmemi istedi.

**Kararım: KABUL.** Şifremi sohbete yazmış olduğum için GitHub'da değiştirmem gerektiği uyarısını da dikkate aldım. Giriş yaptıktan sonra YZ depo türünü sordu; **public + GitHub noreply e-postası** seçtim ki gerçek e-posta adresim herkese açık commit'lerde görünmesin. YZ commit yazarını noreply adresiyle yeniden yazdı, `denizalbayrk/ilac-hatirlatici` deposunu oluşturdu ve `main` dalını push etti. Push'tan önce dosyalarda kişisel e-posta kalmadığını doğruladı.
