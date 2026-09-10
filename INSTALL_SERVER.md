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

## 2. Upload dan extract ZIP
```bash
sudo mkdir -p /opt/bos-syams
sudo chown $USER:$USER /opt/bos-syams
cd /opt/bos-syams
unzip BOS_SYAMS_ALL_IN_V0.2.zip
cd BOS_SYAMS_ALL_IN_V0.2
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
2. Upload source versi baru.
3. Pertahankan `.env`.
4. Jalankan:
```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

## Backup manual
```bash
set -a; . ./.env; set +a
./deploy/backup.sh
```

## Restore
```bash
gunzip -c backups/NAMA_BACKUP.sql.gz | docker compose --env-file .env -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

## Jika belum punya domain
Untuk testing gunakan docker-compose.yml biasa:
```bash
cp .env.example .env
docker compose up -d --build
```
Akses `http://IP-SERVER:8080`.
Pastikan firewall membuka 8080 jika testing. Untuk production gunakan domain + HTTPS.
