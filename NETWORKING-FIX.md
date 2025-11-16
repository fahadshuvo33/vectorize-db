# Docker Networking Fix for CachyOS/Arch

## Problem
Docker is failing with iptables errors:
```
Extension DNAT revision 0 not supported, missing kernel module?
iptables v1.8.11 (nf_tables): RULE_APPEND failed
```

## Quick Fix (Temporary)
Port mappings have been commented out in `docker-compose.yml`. Containers can still communicate via Docker network.

## Permanent Fix

### Option 1: Install iptables-nft (Recommended)
```bash
sudo pacman -S iptables-nft
sudo systemctl restart docker
```

### Option 2: Use host networking (Alternative)
Edit `docker-compose.yml` and add `network_mode: host` to services (not recommended for production).

### Option 3: Fix kernel modules
```bash
sudo modprobe iptable_nat
sudo modprobe ip6table_nat
sudo modprobe iptable_filter
sudo systemctl restart docker
```

### Option 4: Use Docker's userland proxy
Add to `/etc/docker/daemon.json`:
```json
{
  "userland-proxy": true
}
```
Then restart Docker: `sudo systemctl restart docker`

## After Fix
Uncomment the port mappings in `docker-compose.yml`:
- Backend: `8000:8000`
- Frontend: `5173:5173`
- Postgres: `5432:5432` (if needed)
- Redis: `6379:6379` (if needed)

## Test
```bash
docker compose up
```

If successful, you should see all containers running and be able to access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

