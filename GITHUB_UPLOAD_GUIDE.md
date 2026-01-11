# 🚀 GitHub'a Yükleme Rehberi (How to Upload)

Tebrikler! Projeniz şu an tertemiz ve profesyonel bir halde. Aşağıdaki adımları izleyerek GitHub'a yükleyebilirsiniz:

### 1. GitHub'da Yeni Depo (Repository) Oluşturun
- [github.com/new](https://github.com/new) adresine gidin.
- Repository name: `tekla-tools` (veya istediğiniz bir isim).
- **Public** seçin.
- **DİKKAT:** "Initialize this repository with..." kısmındaki seçeneklerin hiçbirini işaretlemeyin (README, gitignore işaretlemeyin, çünkü biz zaten oluşturduk).
- "Create repository" butonuna basın.

### 2. Komut Satırı ile Yükleme
Proje klasörünüzde (`c:\Users\DeAtHeR-Win\Desktop\TEKLA API`) bir terminal (PowerShell) açın ve şu komutları sırayla çalıştırın:

```powershell
# Git'i başlatın
git init

# Tüm dosyaları hazırlayın
git add .

# İlk commit'i yapın
git commit -m "Initial commit: Professional restucture for GitHub"

# GitHub adresinizi bağlayın (GitHub sayfasındaki linki buraya yapıştırın)
# Örn: git remote add origin https://github.com/kullanici_adiniz/tekla-tools.git
git remote add origin <GITHUB_URL_BURAYA>

# Ana dalı belirleyin
git branch -M main

# Dosyaları gönderin
git push -u origin main
```

---

### 🔥 Neden Bu Hal En İyisi?
- **Gizlilik:** `.gitignore` sayesinde gereksiz loglar, `.venv` ve şahsi ayarlarınız GitHub'a gitmez.
- **Profesyonellik:** `README.md` ve `LICENSE` sayesinde projeniz "ben buradayım" der.
- **Düzen:** Tüm görseller ve dökümanlar kendi klasörlerinde, ana dizin tertemiz!
