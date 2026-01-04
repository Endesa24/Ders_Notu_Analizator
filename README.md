# 📄 Ders Notu Analizatörü

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)

**Ders Notu Analizatörü**, uzun ve karmaşık PDF ders notlarını, akademik makaleleri veya kitapları saniyeler içinde analiz eden, özetleyen ve görselleştiren Python tabanlı bir masaüstü uygulamasıdır.

Bu proje, **Nesne Yönelimli Programlama (OOP)** prensipleri, **Doğal Dil İşleme (NLP)** teknikleri ve **Multithreading** mimarisi kullanılarak geliştirilmiştir.

---

## 🚀 Özellikler

* **PDF Analizi:** PDF dosyalarından metin madenciliği yapar, satır sonu hatalarını (hyphenation) otomatik düzeltir.
* **NLP Motoru:** Metni temizler, etkisiz kelimeleri (stopwords) ayıklar ve kök/gövde analizi yapar.
* **Zorluk Derecesi Hesaplama:** Metnin akademik zorluk seviyesini (Kolay/Eğitsel/Akademik) matematiksel formüllerle (Flesch-Kincaid mantığı) puanlar.
* **Otomatik Özetleme:** Frekans tabanlı algoritma ile metnin en önemli cümlelerini belirleyip özet çıkarır.
* **Veri Görselleştirme:**
    * 📊 **Frekans Grafiği:** En sık geçen kavramları sütun grafiği olarak çizer.
    * ☁️ **Kelime Bulutu:** Metnin odak noktalarını WordCloud olarak gösterir.
* **Akıllı Sözlük (Wikipedia Entegrasyonu):** Metindeki teknik terimleri tespit eder ve Wikipedia API üzerinden tanımlarını çeker.
* **Modern Arayüz (GUI):** Tkinter ve Ttk kullanılarak tasarlanmış, sekmeli ve "Dashboard" mantığında çalışan kullanıcı dostu arayüz.
* **Multithreading:** Uzun süren analiz ve internet sorguları arka planda (Daemon Thread) yapılarak arayüzün donması engellenir.

---

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

Bu proje **Python** dili ile geliştirilmiştir ve aşağıdaki kütüphaneleri kullanır:

| Kütüphane | Amaç |
| :--- | :--- |
| **Tkinter & Ttk** | Grafik Kullanıcı Arayüzü (GUI) tasarımı. |
| **PyPDF2** | PDF dosya okuma ve veri çıkarma. |
| **NLTK** | Doğal Dil İşleme (Tokenization, Stopwords). |
| **Matplotlib** | Grafik çizimi ve görselleştirme. |
| **WordCloud** | Kelime bulutu oluşturma. |
| **Wikipedia** | Kavram tanımları için veri çekme. |
| **Threading** | Asenkron işlem yönetimi (Arayüz donmasını önleme). |
| **Collections & Heapq**| Veri yapıları ve algoritma optimizasyonu. |

---

## 🏗️ Proje Mimarisi (OOP Tasarımı)

Proje, **Modülerlik** ve **Kapsülleme** ilkelerine uygun olarak 4 ana sınıfa ayrılmıştır:

1.  **`PDFOkuyucu` (Data Access Layer):**
    * Dosya okuma işlemlerini yönetir.
    * Statik metotlar ile nesne bağımlılığını azaltır.
2.  **`MetinMotoru` (Business Logic Layer):**
    * Projenin beynidir. Metin temizleme, zorluk hesaplama ve özetleme algoritmalarını içerir.
3.  **`GorselRessam` (Visualization Layer):**
    * Matplotlib ve WordCloud işlemlerini yürütür.
4.  **`ModernArayuz` (Presentation Layer):**
    * Kullanıcı etkileşimini yönetir.
    * Thread yönetimini sağlar.
    * Diğer tüm sınıfları koordine eder (Orchestration).

---

## 💻 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

### 1. Projeyi Klonlayın
Terminali açın ve projeyi bilgisayarınıza indirin:
```bash
git clone [https://github.com/Endesa24/akilli-ders-asistani.git](https://github.com/Endesa24/akilli-ders-asistani.git)
cd akilli-ders-asistani
