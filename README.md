---
# DERS NOTU ANALİZATÖRÜ
---
## **Proje:**
Ders_Notu_Analizator uzun ve karmaşık PDF ders notlarını, akademik makaleleri veya kitapları saniyeler içinde analiz eden, özetleyen ve görselleştiren Python tabanlı bir masaüstü uygulamasıdır.

Bu proje, Nesne Yönelimli Programlama (OOP) prensipleri, Doğal Dil İşleme (NLP) teknikleri ve Multithreading mimarisi kullanılarak geliştirilmiştir.

# **Özellikleri:**
* **PDF Analizi:** 
PDF dosyalarından metin madenciliği yapar, satır sonu hatalarını (hyphenation) otomatik düzeltir.

* **NLP Motoru:**
Metni temizler, etkisiz kelimeleri (stopwords) ayıklar ve kök/gövde analizi yapar.

* **Zorluk Derecesi Hesaplama:**
Metnin akademik zorluk seviyesini (Kolay/Eğitsel/Akademik) matematiksel formüllerle (Flesch-Kincaid mantığı) puanlar.

* **Otomatik Özetleme:** 
Frekans tabanlı algoritma ile metnin en önemli cümlelerini belirleyip özet çıkarır.

* **Veri Görselleştirme:**

   * **Frekans Grafiği:** En sık geçen kavramları sütun grafiği olarak çizer.

   * **Kelime Bulutu:** Metnin odak noktalarını WordCloud olarak gösterir.
* **Akıllı Sözlük (Wikipedia Entegrasyonu):**
Metindeki teknik terimleri tespit eder ve Wikipedia API üzerinden tanımlarını çeker. 
* **Modern Arayüz (GUI):** Tkinter ve Ttk kullanılarak tasarlanmış, sekmeli ve "Dashboard" mantığında çalışan kullanıcı dostu arayüz.
* **Multithreading:** Uzun süren analiz ve internet sorguları arka planda (Daemon Thread) yapılarak arayüzün donması engellenir.
---
## Kullanılan Kütüphaneler
|Kütüphane|Kullanım|
| :--- | :--- |
|Tkinter & Ttk|Grafik Kullanıcı Arayüzü (GUI) tasarımı.|
|PyPDF2|PDF dosya okuma ve veri çıkarma.|
|NLTK|Doğal Dil İşleme (Tokenization, Stopwords).|
|
