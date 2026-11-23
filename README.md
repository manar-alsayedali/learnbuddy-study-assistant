# LearnBuddy — Yapay Zeka Destekli Ders Yardımcısı

LearnBuddy, öğrencinin seçtiği derse, çalışma hedefine ve bilgi seviyesine göre kişiselleştirilmiş çalışma planı oluşturur. Beş adımlı planda konu anlatımı için kaynak önerileri ve örnek sorular yer alır. Öğrenci planlarını hesabına kaydedebilir, ilerlemesini takip edebilir ve tamamladığı veya artık ihtiyaç duymadığı planları silebilir.

## Proje raporu özeti

LearnBuddy, Sakarya Üniversitesi Bilgisayar Mühendisliği Yapay Zeka dersi kapsamında geliştirildi. Amaç, öğrencilerin kendi seviyelerine uygun bir çalışma planı hazırlamak ve kaynak bulmak için harcadıkları süreyi azaltmaktı.

Arayüz Streamlit ile yazıldı. Firebase Authentication e-posta ve parola ile kayıt ve giriş işlemlerini yönetir. Uygulama ders, hedef ve seviye seçimlerinden bir istem oluşturup OpenAI API'ye gönderir. Plan ve ilerleme verileri Firebase Realtime Database'de kullanıcının kimliğine bağlı olarak saklanır. Proje Python ile geliştirilmiştir.

## Kurulum

Python 3.13 ile doğrulandı.

```bash
git clone https://github.com/manar-alsayedali/learnbuddy-study-assistant.git
cd learnbuddy-study-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Windows PowerShell’de ortamı etkinleştirmek için `.\.venv\Scripts\Activate.ps1`, şablonu kopyalamak için `Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml` komutunu çalıştırın.

1. Firebase Console'da bir proje ve bir Web uygulaması oluşturun.
2. **Authentication → Sign-in method** bölümünde **Email/Password** sağlayıcısını etkinleştirin.
3. **Realtime Database** oluşturun ve projenin veritabanı URL'sini alın. **Rules** sekmesinde [database.rules.json](database.rules.json) içeriğini yayımlayın. Kurallar, her kullanıcının yalnızca kendi `/users/<uid>` yoluna erişmesine izin verir. [Firebase güvenlik kuralları](https://firebase.google.com/docs/database/security/rules-conditions)
4. `.streamlit/secrets.toml` içindeki `[firebase]` alanlarını Web uygulamanızın yapılandırmasıyla doldurun. `databaseURL` alanına Realtime Database URL'sini yazın.
5. Aynı dosyanın üst kısmında `OPENAI_API_KEY` değerini doldurun. Varsayılan model `gpt-3.5-turbo`. Hesabınızda kullanılabilen başka bir Chat Completions modeli seçmek için `[firebase]` başlığından önce `OPENAI_MODEL` değerini ayarlayın.

```bash
python -m streamlit run app.py
```

Tarayıcıda `http://localhost:8501` adresini açın. **Hesap Oluştur** ile kayıt olun ve giriş yapın. Dersinizi, hedefinizi ve seviyenizi seçip **Yapay Zeka ile Plan Oluştur** düğmesine basın. **Planlarımı Göster** bölümünden bir plan seçerek içeriğini ve ilerlemenizi görebilirsiniz.

Gerçek anahtarları yalnızca yerel `.streamlit/secrets.toml` dosyasına girin. Git, bu dosyayı yok sayar. Depodaki `.example` dosyası boş bir şablondur.

Önceki sürümde e-postaya göre kaydedilmiş planlarınız varsa veritabanı yöneticisi ilgili kayıtları, hesabın Firebase Authentication UID'sine karşılık gelen `/users/<uid>` yoluna taşımalıdır. Uygulama bu taşıma işlemini otomatik yapmaz.
