#!/usr/bin/env bash
#
# Build Bitgesell Core Windows installer
#
# Uses the depends system to cross-compile for x86_64-w64-mingw32,
# then packages the binaries into an NSIS-based installer (.exe).
#
# Prerequisites:
#   - Linux build host (Debian/Ubuntu recommended)
#   - makensis (NSIS) installed for the build host
#   - The depends system prerequisites (see depends/README.md)
#

export LC_ALL=C
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DISTNAME="bitgesell"
VERSION="0.1.13.0"
VERSION_COMMA="0,1,13,0"
BUILD_DIR="${PROJECT_ROOT}/build/installer"

# Parse args
MAKEOPTS="${MAKEOPTS:--j$(nproc)}"
CONFIG_FLAGS=""
CLEAN_BUILD=false

while getopts "v:j:c" opt; do
  case "$opt" in
    v) VERSION="$OPTARG"
       VERSION_COMMA="$(echo "$VERSION" | tr '.' ',')" ;;
    j) MAKEOPTS="-j$OPTARG" ;;
    c) CLEAN_BUILD=true ;;
  esac
done

HOST=x86_64-w64-mingw32
DEPENDS_DIR="${PROJECT_ROOT}/depends"
INSTALL_DIR="${BUILD_DIR}/install"
DEPLOY_DIR="${BUILD_DIR}/deploy"
STAGING_DIR="${DEPLOY_DIR}/${DISTNAME}-${VERSION}-win64"

# --- Step 1: Cross-compile using depends system ---
echo "=== Building Bitgesell Core for ${HOST} ==="

if [ "$CLEAN_BUILD" = true ] && [ -d "${DEPENDS_DIR}/work" ]; then
  echo "Cleaning depends build artifacts..."
  rm -rf "${DEPENDS_DIR}/work"
fi

cd "$PROJECT_ROOT"
./autogen.sh

make "$MAKEOPTS" -C "$DEPENDS_DIR" HOST="$HOST" \
  NO_QT=0 \
  NO_WALLET=0 \
  NO_UPNP=0 \
  NO_NATPMP=0 \
  NO_ZMQ=0

# --- Step 2: Configure and build ---
echo "=== Configuring Bitgesell Core ==="

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

"${PROJECT_ROOT}/configure" \
  --prefix="${DEPENDS_DIR}/${HOST}" \
  --host="$HOST" \
  --with-qt-plugindir="${DEPENDS_DIR}/${HOST}/plugins" \
  --enable-static \
  --disable-shared \
  --with-pic \
  --enable-upnp-default \
  --enable-natpmp-default \
  --with-gui=qt5 \
  $CONFIG_FLAGS

echo "=== Building Bitgesell Core ==="
make "$MAKEOPTS"

# --- Step 3: Stage binaries for installer ---
echo "=== Staging installer files ==="
mkdir -p "${STAGING_DIR}/bin"
mkdir -p "${STAGING_DIR}/doc"

# Copy built binaries
make install DESTDIR="${INSTALL_DIR}"

cp "${BUILD_DIR}/src/qt/BGL-qt.exe"    "${STAGING_DIR}/bin/"
cp "${BUILD_DIR}/src/BGLd.exe"         "${STAGING_DIR}/bin/"
cp "${BUILD_DIR}/src/BGL-cli.exe"      "${STAGING_DIR}/bin/"
cp "${BUILD_DIR}/src/BGL-tx.exe"       "${STAGING_DIR}/bin/"
cp "${BUILD_DIR}/src/BGL-wallet.exe"   "${STAGING_DIR}/bin/"

# Copy supporting files
cp "${PROJECT_ROOT}/COPYING"           "${STAGING_DIR}/"
cp "${PROJECT_ROOT}/doc/README_windows.txt" "${STAGING_DIR}/" 2>/dev/null || true

# Strip debugging symbols
echo "=== Stripping binaries ==="
${HOST}-strip "${STAGING_DIR}/bin/"*.exe

# --- Step 4: Build NSIS installer ---
echo "=== Building NSIS installer ==="

# Check for makensis
if ! command -v makensis &>/dev/null; then
  echo "ERROR: makensis (NSIS) not found. Install with: sudo apt install nsis"
  exit 1
fi

INSTALLER_OUT="${BUILD_DIR}/${DISTNAME}-${VERSION}-win64-setup.exe"

makensis -V4 \
  -DPROJECT_ROOT="${PROJECT_ROOT}" \
  -DDEPLOY_DIR="${STAGING_DIR}" \
  -DVERSION="${VERSION}" \
  -DVERSION_COMMA="${VERSION_COMMA}" \
  -DINSTALLER_OUT="${INSTALLER_OUT}" \
  "${SCRIPT_DIR}/bitgesell.nsi"

echo ""
echo "=== Build complete ==="
echo "Installer: ${INSTALLER_OUT}"
echo "Size: $(ls -lh "${INSTALLER_OUT}" | awk '{print $5}')"
echo ""
echo "SHA256: $(sha256sum "${INSTALLER_OUT}" | awk '{print $1}')"
