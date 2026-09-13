# INSTALL SERVER — BOS SYAMS ALL-IN V0.2

## Pilihan yang disarankan
Ubuntu 22.04/24.04, 2 vCPU, RAM 4 GB+, disk 40 GB+, domain diarahkan ke IP server.

## 1. Install Docker
```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```
Logout/login sekali.

## 2. Ambil source dari GitHub
```bash
sudo mkdir -p /opt/bos-syams
sudo chown $USER:$USER /opt/bos-syams
git clone https://github.com/rizkyzaneva-sukses/bos-syams.git /opt/bos-syams
cd /opt/bos-syams
```

## 3. Buat environment production
```bash
cp .env.prod.example .env
nano .env
```
Ganti DATABASE PASSWORD, SECRET_KEY, dan DOMAIN.

Secret cepat:
```bash
openssl rand -hex 48
```

## 4. DNS
Buat A record `bos.domainanda.com` ke public IP server.

## 5. Jalankan
```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

## 6. Cek
```bash
docker compose --env-file .env -f docker-compose.prod.yml ps
docker compose --env-file .env -f docker-compose.prod.yml logs -f --tail=100
```
Buka `https://DOMAIN_ANDA`.

## Update versi berikutnya
1. Backup database.
2. Ambil source versi baru dengan `git pull --ff-only`.
3. Pertahankan `.env`.
4. Jalankan:
```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

## Backup, restore test, offsite, dan retensi
Pasang `rclone` dan konfigurasikan remote terenkripsi yang terpisah dari server. Jalankan backup harian lewat cron/systemd timer; simpan konfigurasi remote di luar repo. Backup otomatis diuji dengan restore ke database sementara sebelum diunggah. Retensi lokal hanya berjalan setelah unggahan offsite berhasil.
```bash
export OFFSITE_REMOTE='remote:bos-syams/production'
export BACKUP_RETENTION_DAYS=30
./deploy/backup.sh
```
Lakukan uji pemulihan offsite berkala dengan mengunduh arsip ke direktori terpisah lalu jalankan:
```bash
rclone copyto remote:bos-syams/production/NAMA_BACKUP.dump backups/NAMA_BACKUP.dump
./deploy/verify_restore.sh backups/NAMA_BACKUP.dump
```
Untuk pemulihan insiden ke database produksi, hentikan penulisan aplikasi, verifikasi file dump, buat database target bersih, dan gunakan `pg_restore --exit-on-error --no-owner --no-acl`. Jangan restore ke database produksi yang masih berisi data. Simpan backup lama hingga pemulihan tervalidasi.

## Jika belum punya domain
Untuk testing gunakan docker-compose.yml biasa:
```bash
cp .env.example .env
docker compose up -d --build
```
Akses `http://IP-SERVER:8080`.
Pastikan firewall membuka 8080 jika testing. Untuk production gunakan domain + HTTPS.
