#!/bin/sh
# Build the .deb natively on a Debian-based system (Linux Mint).
# Run from the repo root: sh frontend/debian/build-deb.sh

set -e

PKGROOT="frontend/debian/pkgroot"

# Recreate packaged frontend source
rm -rf "$PKGROOT/usr/lib/chess-club-manager/chess_club_fe"
mkdir -p "$PKGROOT/usr/lib/chess-club-manager"

cp -r frontend/chess_club_fe \
    "$PKGROOT/usr/lib/chess-club-manager/chess_club_fe"

# Build Debian package
dpkg-deb --build --root-owner-group "$PKGROOT" \
    frontend/debian/chess-club-manager_1.0.0_all.deb

echo "Built: frontend/debian/chess-club-manager_1.0.0_all.deb"
