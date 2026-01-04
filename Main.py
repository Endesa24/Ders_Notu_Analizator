import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import matplotlib
# KRİTİK AYAR: Matplotlib normalde kendi penceresini açmaya çalışır. 
# "TkAgg" backend'i ile grafikleri Tkinter penceresi içine gömeceğimizi söylüyoruz.
# Bunu yapmazsan program grafik çizerken donabilir.
matplotlib.use("TkAgg") 
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import threading
import wikipedia
import re
from matplotlib.ticker import MaxNLocator
import heapq

# =============================================================================
# 1. KATMAN: İŞ MANTIĞI (BUSINESS LOGIC)
# Bu sınıflar GUI'den (Arayüzden) bağımsızdır. Sadece veri işler.
# =============================================================================

class BilgiUzmani:
    """Wikipedia üzerinden kavram taraması yapan sınıf."""
    def __init__(self):
        try: 
            # Dili Türkçe'ye ayarla. İnternet yoksa hata verebilir, try-except ile geçiyoruz.
            wikipedia.set_lang("tr")
        except: pass

    def kavram_aciklamasi_getir(self, kelime):
        try:
            # Wikipedia'dan sadece ilk 2 cümleyi çekiyoruz (özet).
            ozet = wikipedia.summary(kelime, sentences=2)
            # Regex ile [1], [2] gibi referans numaralarını metinden siliyoruz.
            return re.sub(r'\[\d+\]', '', ozet)
        except: return None

class PDFOkuyucu:
    """PDF dosyasını metne çeviren sınıf."""
    @staticmethod
    def dosya_oku(dosya_yolu, sayfa_limiti=50):
        try:
            reader = PyPDF2.PdfReader(dosya_yolu)
            text = ""
            # Tüm kitabı okumak uzun sürer, bu yüzden bir limit koyuyoruz (örn: 50 sayfa).
            okunacak_sayfa = min(len(reader.pages), sayfa_limiti)
            
            for i in range(okunacak_sayfa):
                extracted = reader.pages[i].extract_text()
                if extracted: 
                    # PDF'lerde satır sonu tireleri (ör: prog- ramlama) kelimeyi böler.
                    # '-\n' ifadesini silerek kelimeyi birleştiriyoruz.
                    extracted = extracted.replace('-\n', '').replace('\n', ' ')
                    text += extracted + " "
            return text
        except Exception as e:
            raise Exception(f"Okuma hatası: {e}")

class MetinMotoru:
    """Doğal Dil İşleme (NLP) işlemlerini yürüten beyin."""
    def __init__(self):
        # Gerekli NLTK veri paketlerini kontrol et, yoksa sessizce indir.
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
        # Etkisiz kelimeleri (ve, veya, ama, the, a, an) hafızaya yükle.
        try:
            tr_stops = set(stopwords.words('turkish'))
            en_stops = set(stopwords.words('english'))
        except OSError:
            tr_stops = set(); en_stops = set()
        
        # Analizden çıkarılacak özel kelimeler ve ekler kümesi.
        inatci_ekler = {"nin", "nın", "nun", "nün", "in", "ın", "un", "ün", "yi", "yı", "yu", "yü", "ye", "ya", "de", "da", "te", "ta", "den", "dan", "ten", "tan", "ki", "si", "sı", "su", "sü", "dir", "dır", "dur", "dür", "leri", "lari", "bölüm", "kısım", "giriş", "sonuç", "kaynakça", "et", "al", "ver", "yap", "ol"}
        ozel_filtreler = {"bir", "bu", "ile", "ve", "veya", "için", "olan", "olarak", "kadar", "gibi", "the", "and", "of", "to", "in", "is", "that", "it", "ne", "var", "yok"}
        
        # Set (küme) kullanarak birleştiriyoruz. Set içinde arama yapmak O(1) hızındadır (çok hızlı).
        self.tum_yasaklar = tr_stops.union(en_stops).union(inatci_ekler).union(ozel_filtreler)

    def metni_temizle(self, ham):
        # Tırnak işaretlerini kaldır.
        ham = ham.replace("'", " ").replace("’", " ").replace("`", " ")
        # Metni kelimelere böl (Tokenization).
        tokens = word_tokenize(ham.lower(), language='turkish')
        # Sadece alfabetik olanları ve yasaklı listede olmayanları al. Uzunluğu 2'den büyük olmalı.
        return [w for w in tokens if w.isalpha() and w not in self.tum_yasaklar and len(w) > 2]

    def zorluk_hesapla(self, ham):
        """Flesch-Kincaid benzeri basit bir okunabilirlik metriği."""
        words = [w for w in word_tokenize(ham) if w.isalnum()]
        if not words: return 0, "---"
        
        # Sesli harfleri sayarak hece tahmini yapıyoruz.
        hece = sum(sum(1 for h in w if h in "aeıioöuüAEIİOÖUÜ") for w in words)
        if len(words) == 0: return 0, "---"
        
        # Formül: (Toplam Hece / Toplam Kelime) oranı arttıkça metin zorlaşır.
        skor = 118.8 - (25.9 * (hece / len(words)))
        
        if skor > 50: return skor, "Kolay / Anlaşılır"
        elif skor > 35: return skor, "Orta / Eğitsel"
        else: return skor, "Zor / Akademik"

    def en_sik_gecenler(self, liste, n=5):
        # Counter sınıfı listeyi tarar ve {kelime: sayı} sözlüğü oluşturur.
        return [x[0] for x in Counter(liste).most_common(n)]

    def metni_utule(self, metin):
        # Noktalama işaretlerinden sonra boşluk yoksa ekle (Regex: Lookbehind & Lookahead).
        metin = re.sub(r'(?<=[.,;!:])(?=[^\s])', r' ', metin)
        # Fazla boşlukları tek boşluğa indir.
        return re.sub(r'\s+', ' ', metin).strip()

    def metni_ozetle(self, ham_metin, cumle_sayisi=5):
        """Frekans tabanlı ekstraktif özetleme algoritması."""
        ham_metin = self.metni_utule(ham_metin)
        try: cumleler = sent_tokenize(ham_metin, language='turkish')
        except: cumleler = ham_metin.split('.')
        
        if len(cumleler) <= cumle_sayisi: return ham_metin
        
        # 1. Adım: Kelime frekanslarını bul.
        frekans = Counter(self.metni_temizle(ham_metin))
        if not frekans: return "Özetlenecek içerik yok."
        
        # 2. Adım: Frekansları normalize et (0 ile 1 arasına çek).
        max_f = max(frekans.values())
        for k in frekans: frekans[k] /= max_f
        
        # 3. Adım: Her cümleye puan ver.
        skorlar = {}
        for cumle in cumleler:
            for kelime in word_tokenize(cumle.lower()):
                if kelime in frekans:
                    # Çok uzun cümleler özet için iyi değildir, filtreliyoruz (<40 kelime).
                    if len(cumle.split()) < 40:
                        skorlar[cumle] = skorlar.get(cumle, 0) + frekans[kelime]
        
        # 4. Adım: En yüksek puanlı N cümleyi seç.
        return " ".join(heapq.nlargest(cumle_sayisi, skorlar, key=skorlar.get))

class GorselRessam:
    """Grafik çizim işlemlerini yapan sınıf."""
    @staticmethod
    def cubuk(liste):
        if not liste: 
            messagebox.showwarning("Uyarı", "Veri yok.")
            return
        try:
            # Önceki çizimleri temizle (bellek yönetimi).
            plt.close('all')
            c = Counter(liste).most_common(10)
            plt.figure(figsize=(10,6))
            # x ekseni kelimeler, y ekseni sayılar.
            plt.bar([x[0] for x in c], [x[1] for x in c], color="#3498db")
            plt.title("En Sık Geçen Kavramlar")
            plt.xticks(rotation=45)
            plt.tight_layout() # Grafiğin kenarlara taşmasını engeller.
            plt.show()
        except Exception as e: messagebox.showerror("Hata", str(e))
    
    @staticmethod
    def bulut(liste):
        if not liste: return
        try:
            plt.close('all')
            # WordCloud kütüphanesi otomatik olarak kelime büyüklüklerini ayarlar.
            wc = WordCloud(width=600, height=400, background_color="white", colormap="viridis").generate_from_frequencies(Counter(liste))
            plt.figure(figsize=(8,5))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off") # Eksen sayılarını gizle.
            plt.show()
        except Exception as e: messagebox.showerror("Hata", str(e))

# =============================================================================
# 2. KATMAN: KULLANICI ARAYÜZÜ (GUI)
# Tkinter kodları burada yer alır.
# =============================================================================

class ModernArayuz:
    # Ana pencere ve widget'ları oluşturur.
    def __init__(self, root):
        self.root = root
        self.root.title("Ders Notu Analizatörü")
        self.root.geometry("1200x800")
        
        # Renk Paleti: Tasarımı tek bir yerden yönetmek için sözlük kullandık.
        self.renkler = {
            "bg_dark": "#2c3e50",    
            "bg_light": "#ecf0f1",   
            "accent": "#e67e22",     
            "btn_normal": "#34495e", 
            "btn_hover": "#1abc9c",  
            "text_white": "#ffffff",
            "text_dark": "#2c3e50"
        }
        
        self.root.configure(bg=self.renkler["bg_light"])
        
        # Mantık motorlarını başlatıyoruz.
        self.okuyucu = PDFOkuyucu()
        self.motor = MetinMotoru()
        self.ressam = GorselRessam()
        self.bilgi = BilgiUzmani()
        
        # Verileri saklayacağımız değişkenler.
        self.ham_metin = ""
        self.temiz_liste = []
        
        self.stili_ayarla()
        self.ekrani_kur()

    def stili_ayarla(self):
        """Tkinter 'ttk' widget'larının görünümünü özelleştirir."""
        style = ttk.Style()
        try: style.theme_use('clam') # Modern görünüm için 'clam' temasını dene.
        except: pass
        
        # Stil tanımları (CSS mantığına benzer).
        style.configure("TFrame", background=self.renkler["bg_light"])
        style.configure("Sidebar.TFrame", background=self.renkler["bg_dark"])
        style.configure("Baslik.TLabel", font=("Segoe UI", 20, "bold"), background=self.renkler["bg_dark"], foreground=self.renkler["text_white"])
        style.configure("AltBaslik.TLabel", font=("Segoe UI", 10), background=self.renkler["bg_dark"], foreground="#bdc3c7")
        style.configure("Durum.TLabel", font=("Segoe UI", 11, "bold"), background=self.renkler["bg_light"], foreground=self.renkler["accent"])
        
        # Buton stilleri ve hover (üzerine gelince) efektleri.
        style.configure("Menu.TButton", font=("Segoe UI", 11), padding=10, background=self.renkler["btn_normal"], foreground="white", borderwidth=0)
        style.map("Menu.TButton", background=[("active", self.renkler["btn_hover"])])
        
        style.configure("Yukle.TButton", font=("Segoe UI", 12, "bold"), padding=15, background=self.renkler["accent"], foreground="white")
        style.map("Yukle.TButton", background=[("active", "#d35400")])

    def ekrani_kur(self):
        """Ekran düzenini (Layout) oluşturur. Grid yerine Pack yöntemi kullanıldı."""
        
        # --- SOL PANEL (SIDEBAR) ---
        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=250)
        sidebar.pack(side="left", fill="y") # Sola yasla, dikeyde doldur.
        
        # Logo ve Başlık
        lbl_baslik = ttk.Label(sidebar, text="Ders Notu \n Analizatörü", style="Baslik.TLabel", justify="center")
        lbl_baslik.pack(pady=(30, 10), padx=20)
        ttk.Label(sidebar, text="v9.0", style="AltBaslik.TLabel").pack(pady=(0, 30))
        
        # Dosya Yükleme Butonu
        self.btn_yukle = ttk.Button(sidebar, text="📄 PDF YÜKLE", style="Yukle.TButton", command=self.baslat_thread)
        self.btn_yukle.pack(fill="x", padx=20, pady=10)
        
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20, pady=20)
        
        # Fonksiyon Butonları (Başlangıçta pasif/disabled)
        self.btn_grafik = ttk.Button(sidebar, text="📊 Frekans Grafiği", style="Menu.TButton", command=lambda: self.ressam.cubuk(self.temiz_liste), state="disabled")
        self.btn_grafik.pack(fill="x", padx=20, pady=5)
        
        self.btn_bulut = ttk.Button(sidebar, text="☁️ Kelime Bulutu", style="Menu.TButton", command=lambda: self.ressam.bulut(self.temiz_liste), state="disabled")
        self.btn_bulut.pack(fill="x", padx=20, pady=5)
        
        self.btn_ozet = ttk.Button(sidebar, text="📝 Makale Özeti", style="Menu.TButton", command=self.ozet_penceresi_ac, state="disabled")
        self.btn_ozet.pack(fill="x", padx=20, pady=5)
        
        self.btn_acikla = ttk.Button(sidebar, text="🧠 Kavram Sözlüğü", style="Menu.TButton", command=self.aciklama_penceresi_ac, state="disabled")
        self.btn_acikla.pack(fill="x", padx=20, pady=5)

        # --- SAĞ PANEL (ANA İÇERİK) ---
        main_area = ttk.Frame(self.root, style="TFrame")
        main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Üst Bilgi Çubuğu
        info_frame = ttk.Frame(main_area, style="TFrame")
        info_frame.pack(fill="x", pady=(0, 20))
        
        self.lbl_durum = ttk.Label(info_frame, text="Başlamak için sol menüden bir PDF yükleyin.", style="Durum.TLabel")
        self.lbl_durum.pack(side="left")
        
        # Sekmeli Yapı (Notebook)
        self.notebook = ttk.Notebook(main_area)
        self.notebook.pack(fill="both", expand=True)
        
        # Sekme 1
        frame_orj = ttk.Frame(self.notebook)
        self.notebook.add(frame_orj, text="  📄 Orijinal Metin  ")
        self.txt_orj = scrolledtext.ScrolledText(frame_orj, font=("Consolas", 11), wrap=tk.WORD, padx=10, pady=10, bd=0)
        self.txt_orj.pack(fill="both", expand=True)
        
        # Sekme 2
        frame_sade = ttk.Frame(self.notebook)
        self.notebook.add(frame_sade, text="  🧹 Sadeleştirilmiş Veri  ")
        self.txt_sade = scrolledtext.ScrolledText(frame_sade, font=("Consolas", 11), wrap=tk.WORD, padx=10, pady=10, bd=0)
        self.txt_sade.pack(fill="both", expand=True)

    def baslat_thread(self):
        """
        Dosya okuma ve analiz uzun sürer. Eğer bunu ana programda yaparsak arayüz donar.
        Bu yüzden 'threading' ile arka planda yeni bir işçi (worker) başlatıyoruz.
        """
        file_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not file_path: return
        
        self.btn_yukle.config(state="disabled")
        self.lbl_durum.config(text="⏳ PDF Analiz ediliyor, lütfen bekleyin...", foreground=self.renkler["accent"])
        self.root.config(cursor="watch") # İmleci bekleme moduna al.
        
        # 'daemon=True' demek, ana program kapanırsa bu thread de ölsün demektir.
        threading.Thread(target=self.islem_yap, args=(file_path,), daemon=True).start()

    def islem_yap(self, yol):
        """Bu fonksiyon ARKA PLANDA (Thread içinde) çalışır."""
        try:
            ham = self.okuyucu.dosya_oku(yol)
            temiz = self.motor.metni_temizle(ham)
            skor, zorluk = self.motor.zorluk_hesapla(ham)
            
            # Sonuçları sınıf değişkenlerine kaydet.
            self.ham_metin = ham
            self.temiz_liste = temiz
            
            # DİKKAT: Thread içinden GUI (Ekran) güncellenmez! Program çöker.
            # 'root.after(0, ...)' komutu ile ana programa "işim bitti, şu fonksiyonu çalıştır" sinyali gönderiyoruz.
            self.root.after(0, lambda: self.guncelle(skor, zorluk))
        except Exception as e:
            self.root.after(0, lambda: self.hata_goster(str(e)))

    def guncelle(self, skor, zorluk):
        """Bu fonksiyon ANA PROGRAMDA çalışır ve ekranı günceller."""
        self.txt_orj.delete(1.0, tk.END)
        self.txt_orj.insert(tk.END, self.ham_metin)
        
        self.txt_sade.delete(1.0, tk.END)
        self.txt_sade.insert(tk.END, " ".join(self.temiz_liste))
        
        self.lbl_durum.config(text=f"✅ Analiz Tamamlandı | Okunabilirlik: {skor:.1f} ({zorluk})", foreground="#27ae60")
        self.btn_yukle.config(state="normal")
        self.root.config(cursor="")
        
        # Butonları tekrar aktif et.
        for btn in [self.btn_grafik, self.btn_bulut, self.btn_acikla, self.btn_ozet]:
            btn.config(state="normal")

    def hata_goster(self, mesaj):
        messagebox.showerror("Hata", mesaj)
        self.lbl_durum.config(text="⚠️ Bir hata oluştu.", foreground="red")
        self.btn_yukle.config(state="normal")
        self.root.config(cursor="")

    # --- GÜVENLİ GUI GÜNCELLEME METOTLARI ---
    # Thread çalışırken kullanıcı pencereyi kapatırsa, kod olmayan pencereye yazmaya çalışır ve hata verir.
    # Bu metotlar "widget.winfo_exists()" ile pencerenin varlığını kontrol eder.
    
    def guvenli_config(self, widget, **kwargs):
        try:
            if widget.winfo_exists(): widget.config(**kwargs)
        except: pass

    def guvenli_ekle(self, widget, metin):
        try:
            if widget.winfo_exists():
                widget.insert(tk.END, metin)
                widget.see(tk.END) # Otomatik kaydırma
        except: pass

    def guvenli_temizle(self, widget):
        try:
            if widget.winfo_exists(): widget.delete(1.0, tk.END)
        except: pass

    # --- PENCERE FONKSİYONLARI ---
    
    def aciklama_penceresi_ac(self):
        popup = tk.Toplevel(self.root)
        popup.title("Kavram Sözlüğü")
        popup.geometry("600x600")
        popup.configure(bg=self.renkler["bg_light"])
        
        tk.Label(popup, text="🔍 Akıllı Kavram Sözlüğü", font=("Segoe UI", 16, "bold"), bg=self.renkler["bg_light"], fg=self.renkler["bg_dark"]).pack(pady=10)
        
        lbl_durum = tk.Label(popup, text="Kavramlar taranıyor...", font=("Segoe UI", 10, "italic"), bg=self.renkler["bg_light"], fg=self.renkler["accent"])
        lbl_durum.pack(pady=2)

        text_area = scrolledtext.ScrolledText(popup, width=60, height=20, font=("Calibri", 11), wrap=tk.WORD, bd=0, padx=10, pady=10)
        text_area.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Yine uzun süren işlem (internet sorgusu) olduğu için thread kullanıyoruz.
        threading.Thread(target=self.anlamlari_bul_yaz, args=(text_area, lbl_durum), daemon=True).start()

    def anlamlari_bul_yaz(self, widget, lbl_durum):
        """Thread içinde çalışır, Wikipedia sorgusu yapar."""
        if not self.temiz_liste: return
        
        kavramlar = self.motor.en_sik_gecenler(self.temiz_liste, 15)
        self.root.after(0, lambda: self.guvenli_temizle(widget))
        
        bulunan = 0
        for k in kavramlar:
            # Pencere kapatıldıysa işlemi durdur.
            try:
                if not widget.winfo_exists(): return
            except: return
            
            if bulunan >= 5: break 

            mesaj = f"🔎 '{k}' aranıyor..."
            self.root.after(0, lambda t=mesaj: self.guvenli_config(lbl_durum, text=t))

            bilgi = self.bilgi.kavram_aciklamasi_getir(k)
            
            if bilgi:
                yeni_metin = f"📌 {k.upper()}\n{bilgi}\n\n{'='*30}\n\n"
                bulunan += 1
                self.root.after(0, lambda t=yeni_metin: self.guvenli_ekle(widget, t))
        
        sonuc_mesaj = "✅ İşlem tamamlandı." if bulunan > 0 else "Kavram bulunamadı."
        self.root.after(0, lambda: self.guvenli_config(lbl_durum, text=sonuc_mesaj, fg="green"))

    def ozet_penceresi_ac(self):
        if not self.ham_metin: return
        
        ozet = self.motor.metni_ozetle(self.ham_metin, 7)
        
        pencere = tk.Toplevel(self.root)
        pencere.title("Makale Özeti")
        pencere.geometry("700x500")
        pencere.configure(bg=self.renkler["bg_light"])
        
        tk.Label(pencere, text="📝 Yapay Zeka Özeti", font=("Segoe UI", 16, "bold"), bg=self.renkler["bg_light"], fg=self.renkler["bg_dark"]).pack(pady=10)
        
        txt = scrolledtext.ScrolledText(pencere, font=("Calibri", 12), wrap=tk.WORD, bd=0, padx=15, pady=15)
        txt.pack(padx=20, pady=20, fill="both", expand=True)
        
        txt.insert(tk.END, ozet)
        txt.configure(state='disabled') # Kullanıcı değiştiremesin diye kilitliyoruz.

if __name__ == "__main__":
    root = tk.Tk()
    # Yüksek DPI (4K ekranlar) için netlik ayarı.
    try: 
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = ModernArayuz(root)
    root.mainloop()
