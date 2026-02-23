"""
VerSig.py - Verificación de Firma Digital con RSA + SHA-256
============================================================
Equivalente Python del programa VerSig.java de Oracle.

Puede usarse desde la terminal O importarse como módulo por app_firma.py.

Uso desde terminal:
    python VerSig.py <llave_publica> <firma> <archivo_original>

Ejemplo:
    python VerSig.py public_key.pem signature.bin data.txt
"""

import sys
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


# ─────────────────────────────────────────────
# FUNCIONES REUTILIZABLES 
# ─────────────────────────────────────────────

def load_public_key(filepath):
    """
    Carga la llave pública desde un archivo PEM.
    Equivalente a KeyFactory + X509EncodedKeySpec en Java.
    """
    print(f"[*] Cargando llave pública desde: {filepath}")
    with open(filepath, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    print("[+] Llave pública cargada exitosamente.")
    return public_key


def load_signature(filepath):
    """Carga los bytes de la firma desde el archivo binario."""
    print(f"[*] Cargando firma digital desde: {filepath}")
    with open(filepath, "rb") as f:
        signature = f.read()
    print(f"[+] Firma cargada ({len(signature)} bytes).")
    return signature


def verify_signature(public_key, signature, data_filepath):
    """
    Verifica la firma digital del archivo.
    Equivalente a sig.verify(sigToVerify) en Java.
    Retorna True si la firma es válida, False si no.
    """
    print(f"[*] Leyendo datos del archivo: {data_filepath}")
    with open(data_filepath, "rb") as f:
        data = f.read()

    print("[*] Verificando firma digital...")
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def verify_file(public_key_path, signature_path, data_path):
    """
    Función de alto nivel que recibe 3 rutas y devuelve True/False.
    Usada principalmente por app_firma.py (GUI).
    """
    public_key = load_public_key(public_key_path)
    signature  = load_signature(signature_path)
    return verify_signature(public_key, signature, data_path)


# ─────────────────────────────────────────────
# MAIN — solo se ejecuta si se corre desde CLI
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) != 4:
        print("Uso: python VerSig.py <llave_publica> <firma> <archivo_datos>")
        print("Ejemplo: python VerSig.py public_key.pem signature.bin data.txt")
        sys.exit(1)

    pubkey_file = sys.argv[1]
    sig_file    = sys.argv[2]
    data_file   = sys.argv[3]

    for f in [pubkey_file, sig_file, data_file]:
        if not os.path.exists(f):
            print(f"[ERROR] No se encontró el archivo: {f}")
            sys.exit(1)

    print("=" * 55)
    print("   VERIFICACIÓN DE FIRMA DIGITAL - RSA + SHA-256")
    print("=" * 55)

    result = verify_file(pubkey_file, sig_file, data_file)

    print("=" * 55)
    if result:
        print("[✓] signature verifies: TRUE")
        print("    El documento es auténtico e íntegro.")
    else:
        print("[✗] signature verifies: FALSE")
        print("    ADVERTENCIA: El documento fue alterado o la firma no corresponde.")
    print("=" * 55)


if __name__ == "__main__":
    main()