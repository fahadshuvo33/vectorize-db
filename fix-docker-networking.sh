#!/bin/bash
# Script to fix Docker networking issues on CachyOS/Arch

echo "Attempting to fix Docker networking issues..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo ./fix-docker-networking.sh"
    exit 1
fi

echo "1. Loading required kernel modules..."
modprobe iptable_nat 2>/dev/null || echo "  ⚠️  iptable_nat module not available"
modprobe ip6table_nat 2>/dev/null || echo "  ⚠️  ip6table_nat module not available"
modprobe iptable_filter 2>/dev/null || echo "  ⚠️  iptable_filter module not available"

echo "2. Checking iptables vs nftables..."
if command -v nft &> /dev/null; then
    echo "  ℹ️  nftables detected"
    # Check if iptables is using nftables backend
    if iptables -V 2>&1 | grep -q nf_tables; then
        echo "  ℹ️  iptables is using nftables backend"
    fi
fi

echo "3. Restarting Docker service..."
systemctl restart docker

echo "4. Waiting for Docker to be ready..."
sleep 3

if systemctl is-active --quiet docker; then
    echo "✅ Docker is running"
    echo ""
    echo "Try running: docker compose up"
    echo ""
    echo "If issues persist, you may need to:"
    echo "  - Install iptables-nft: sudo pacman -S iptables-nft"
    echo "  - Or configure Docker to use a different networking backend"
else
    echo "❌ Docker failed to start. Check logs: sudo journalctl -u docker -n 50"
fi

