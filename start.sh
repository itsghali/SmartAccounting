#!/bin/bash
# ============================================
#  EasyAccounting SaaS — Lancement unique
# ============================================

set -e

echo "=========================================="
echo "  EasyAccounting SaaS - Demarrage"
echo "=========================================="

# Verifier que Docker est lance
if ! docker info > /dev/null 2>&1; then
  echo "ERREUR: Docker n'est pas lance. Demarrez Docker Desktop d'abord."
  exit 1
fi

cd "$(dirname "$0")"

# Build et lancement de tous les services
echo ""
echo "[1/2] Build des images..."
docker compose build

echo ""
echo "[2/2] Demarrage des services..."
docker compose up -d

echo ""
echo "=========================================="
echo "  Tous les services sont lances !"
echo "=========================================="
echo ""
echo "  Frontend :  http://localhost:3000"
echo "  API :       http://localhost:8000"
echo "  API Docs :  http://localhost:8000/docs"
echo "  MinIO :     http://localhost:9001"
echo ""
echo "  Logs : docker compose logs -f"
echo "  Stop : docker compose down"
echo "=========================================="
