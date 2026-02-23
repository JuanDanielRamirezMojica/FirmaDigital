"""
GenSig.py - Generación de Firma Digital con RSA + SHA-256
==========================================================
Equivalente Python del programa GenSig.java de Oracle.

Puede usarse desde la terminal O importarse como módulo por app_firma.py.

Uso desde terminal:
    python GenSig.py <archivo_a_firmar>

Salida:
    public_key.pem   -> Llave pública (formato PEM/X.509)
    private_key.pem  -> Llave privada cifrada (opcional)
    signature.bin    -> Firma digital del archivo
"""

import sys
import os
import getpass
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


# ─────────────────────────────────────────────
# FUNCIONES REUTILIZABLES (usadas por CLI y GUI)
# ─────────────────────────────────────────────

def generate_keys():
    """Genera un par de llaves RSA de 2048 bits."""
    print("[*] Generando par de llaves RSA 2048-bit...")
    private_key = rsa.generate_private_key(
        # 65537 es el exponente público estándar universal
        public_exponent=65537,
        # Tamaño de llave: 2048 = estándar actual (256 bytes de firma)
        key_size=2048,
    )
    public_key = private_key.public_key()
    print("[+] Par de llaves generado exitosamente.")
    return private_key, public_key


def load_private_key(filepath, password=None):
    """
    Carga una llave privada existente desde un archivo PEM.
    - Si password=None, la pide por consola (modo CLI).
    - Si password se pasa como string, la usa directamente (modo GUI).
    """
    print(f"[*] Cargando llave privada desde: {filepath}")
    if password is None:
        password = getpass.getpass("    Ingresa la contraseña de la llave privada: ")
    with open(filepath, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password.encode())
    print("[+] Llave privada cargada exitosamente.")
    return private_key


def save_private_key(private_key, filename="private_key.pem", password=None):
    """
    Guarda la llave privada cifrada con contraseña.
    - Si password=None, la pide por consola (modo CLI).
    - Si password se pasa como string, la usa directamente (modo GUI).
    """
    if password is None:
        print("[*] Para proteger tu llave privada, ingresa una contraseña:")
        while True:
            password = getpass.getpass("    Contraseña: ")
            confirmacion = getpass.getpass("    Confirmar contraseña: ")
            if password == confirmacion:
                break
            print("[!] Las contraseñas no coinciden, intenta de nuevo.")

    with open(filename, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        ))
    print(f"[+] Llave privada guardada en: {filename}")


def save_public_key(public_key, filename="public_key.pem"):
    """Guarda la llave pública en formato PEM (X.509/SubjectPublicKeyInfo)."""
    pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, "wb") as f:
        f.write(pem_bytes)
    print(f"[+] Llave pública guardada en: {filename}")


def sign_file(private_key, filepath):
    """Firma el contenido de un archivo usando RSA-PSS con SHA-256."""
    print(f"[*] Leyendo archivo a firmar: {filepath}")
    with open(filepath, "rb") as f:
        data = f.read()

    print("[*] Generando firma digital (RSA + SHA-256)...")
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("[+] Firma digital generada exitosamente.")
    return signature


def save_signature(signature, filename="signature.bin"):
    """Guarda los bytes de la firma digital en un archivo binario."""
    with open(filename, "wb") as f:
        f.write(signature)
    print(f"[+] Firma digital guardada en: {filename}")
    print(f"    Tamaño de la firma: {len(signature)} bytes ({len(signature)*8} bits)")


# ─────────────────────────────────────────────
# MAIN — solo se ejecuta si se corre desde CLI
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Uso: python GenSig.py <archivo_a_firmar>")
        print("Ejemplo: python GenSig.py data.txt")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"[ERROR] No se encontró el archivo: {filepath}")
        sys.exit(1)

    print("=" * 55)
    print("   GENERACIÓN DE FIRMA DIGITAL - RSA + SHA-256")
    print("=" * 55)

    llave_existente = False
    if os.path.exists("private_key.pem"):
        print("[?] Se encontró una llave privada existente (private_key.pem)")
        respuesta = input("    ¿Deseas usarla? (s/n): ").strip().lower()
        llave_existente = respuesta == "s"

    if llave_existente:
        try:
            private_key = load_private_key("private_key.pem")  # pide contraseña por consola
            public_key = private_key.public_key()
            save_public_key(public_key, "public_key.pem")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar la llave privada: {e}")
            sys.exit(1)
    else:
        private_key, public_key = generate_keys()
        respuesta = input("[?] ¿Deseas guardar la llave privada para usarla después? (s/n): ").strip().lower()
        if respuesta == "s":
            save_private_key(private_key)  # pide contraseña por consola
        save_public_key(public_key, "public_key.pem")

    signature = sign_file(private_key, filepath)
    save_signature(signature, "signature.bin")

    print("=" * 55)
    print("[✓] Proceso completado. Archivos generados:")
    print("    - public_key.pem  (llave pública)")
    print("    - signature.bin   (firma digital)")
    print("=" * 55)


if __name__ == "__main__":
    main()