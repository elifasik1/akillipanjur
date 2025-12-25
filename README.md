# 🏠 Akıllı Panjur Otomasyon Sistemi

Bu proje, IoT tabanlı bir akıllı panjur kontrol sisteminin web tabanlı bir dashboard üzerinden yönetimini ve sensör verilerinin (Işık, Sıcaklık, Nem) gerçek zamanlı analizini kapsayan bir **Bilgisayar Mühendisliği** çalışmasıdır.

## 🚀 Proje Özellikleri

- **Gerçek Zamanlı Veri İzleme:** Sensörlerden gelen veriler anlık olarak Chart.js ile görselleştirilir.
- **Akıllı Karar Mekanizması:** Sıcaklık ve ışık şiddeti eşik değerlerine göre panjur otomatik olarak konumlanır.
- **Manuel ve Otomatik Mod:** Kullanıcı panel üzerinden sistemi manuel kontrol edebilir veya algoritmaya bırakabilir.
- **Veri Kalıcılığı:** Gelen tüm sensör verileri ve sistem durumları SQLite veritabanında saklanır.
- **Modern UI/UX:** Responsive tasarım ile mobil ve masaüstü uyumlu kullanıcı arayüzü.

## 🛠️ Kullanılan Teknolojiler

- **Backend:** Python (Flask Framework)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Veritabanı:** SQLite
- **Grafik Kütüphanesi:** Chart.js
- **Haberleşme:** REST API (JSON)

## 📁 Proje Yapısı

```text
akillipanjur/
├── backend/
│   ├── app.py          # Ana Flask sunucusu ve API endpointleri
│   ├── db.py           # Veritabanı işlemleri (CRUD)
│   └── panjur.db       # SQLite veritabanı dosyası
├── frontend/
│   ├── index.html      # Kullanıcı arayüzü
│   ├── style.css       # Tasarım dosyaları
│   └── app.js          # Frontend mantığı ve API haberleşmesi
└── README.md           # Proje dökümantasyonu
