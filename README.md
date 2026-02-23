# 🔐 Firma Digital RSA

Implementación de firma digital usando **RSA + SHA-256** en Python.  
Equivalente al programa `GenSig.java` / `VerSig.java` de la guía oficial de Oracle.

Disponible en dos modos: **línea de comandos (CLI)** e **interfaz gráfica (GUI)**.

---

## ¿Qué es una firma digital?

Una firma digital **no cifra ni oculta** el documento. Lo que hace es garantizar dos cosas:

- **Autenticidad** — el documento fue firmado por quien tiene la llave privada
- **Integridad** — el documento no fue modificado después de ser firmado

Si alguien cambia aunque sea un espacio del documento, la verificación falla.

---

## ¿Cómo funciona por dentro?

### Al firmar (`GenSig.py`):
1. Se genera un par de llaves RSA de 2048 bits (pública y privada)
2. Se calcula el hash SHA-256 del documento — una "huella digital" única del contenido
3. Se cifra ese hash con la llave privada → ese resultado es la firma
4. La firma se guarda en `signature.bin` y la llave pública en `public_key.pem`
5. El documento original **no se modifica**

### Al verificar (`VerSig.py`):
1. Se descifra la firma usando la llave pública → se obtiene el hash original
2. Se recalcula el hash SHA-256 del documento recibido
3. Se comparan los dos hashes — si coinciden: `TRUE`, si no: `FALSE`

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `GenSig.py` | Lógica de generación de llaves y firma — usable como CLI o módulo |
| `VerSig.py` | Lógica de verificación — usable como CLI o módulo |
| `app_firma.py` | Interfaz gráfica — importa su lógica de `GenSig.py` y `VerSig.py` |
| `data.txt` | Documento de ejemplo a firmar |
| `public_key.pem` | Llave pública generada (formato X.509/PEM) |
| `signature.bin` | Firma digital binaria (256 bytes = 2048 bits) |

---

## Requisitos

- Python 3.x
- Librería `cryptography`

```bash
pip install cryptography
```

---

## Uso — CLI (línea de comandos)

### 1. Firmar un documento

```bash
python GenSig.py data.txt
```

El programa preguntará si existe una llave privada guardada o si generar una nueva, y si deseas guardarla para uso futuro.

**Archivos generados:**
- `public_key.pem` — llave pública, compártela libremente
- `signature.bin` — la firma digital del documento
- `private_key.pem` — llave privada cifrada (solo si decides guardarla)

### 2. Verificar una firma

```bash
python VerSig.py public_key.pem signature.bin data.txt
```

**Resultado:**
```
[✓] signature verifies: TRUE   → documento auténtico e íntegro
[✗] signature verifies: FALSE  → documento alterado o firma inválida
```

---

## Uso — GUI (interfaz gráfica)

```bash
python app_firma.py
```

No requiere instalar nada extra — usa `tkinter` que viene incluido con Python.

La ventana tiene dos pestañas:

**Pestaña FIRMAR:**
- Clic en la zona para seleccionar cualquier archivo
- Opción de cargar una llave privada existente (`private_key.pem`) o generar una nueva
- Si generas una nueva, el programa pregunta si deseas guardarla para reutilizarla
- Los archivos generados (`public_key.pem` y `signature.bin`) se guardan en la misma carpeta del documento

**Pestaña VERIFICAR:**
- Seleccionar los 3 archivos: llave pública, firma y documento
- El resultado se muestra en pantalla — verde si es válido, rojo si no

### Arquitectura del front

`app_firma.py` **no contiene lógica criptográfica**. Solo es la interfaz visual. Importa todo desde los módulos CLI:

```python
from GenSig import generate_keys, sign_file, save_public_key, save_private_key, load_private_key, save_signature
from VerSig import verify_file
```

Esto significa que los tres archivos deben estar en la misma carpeta para que funcione.

---

## Flujo completo

```
FIRMAR                          VERIFICAR
──────                          ─────────
data.txt ──┐                    data.txt ──┐
           ├─► GenSig.py ──►   public_key.pem ──┤─► VerSig.py ──► TRUE/FALSE
llave      │                    signature.bin ──┘
privada ───┘
    │
    ▼
public_key.pem
signature.bin
```

---

## Preguntas frecuentes

**¿El documento se modifica al firmarlo?**  
No. El documento original queda intacto. La firma vive en `signature.bin`, que es un archivo separado.

**¿Qué le mando a la otra persona para que verifique?**  
Los 3 archivos: `data.txt` + `public_key.pem` + `signature.bin`.

**¿Cada documento tiene una firma única?**  
Sí. Y además el mismo documento firmado dos veces genera firmas diferentes (por el salt aleatorio del algoritmo PSS), aunque las dos son válidas.

**¿Puedo firmar cualquier tipo de archivo?**  
Sí — PDF, imagen, ejecutable, lo que sea. El programa lee el archivo en bytes.

```bash
python GenSig.py contrato.pdf
python GenSig.py foto.jpg
```

**¿Qué pasa si alguien roba mi `signature.bin`?**  
No puede hacer nada con ella. Esa firma solo es válida para ese documento específico. No le permite generar firmas nuevas porque para eso necesitaría la llave privada.

**¿Por qué la firma pesa exactamente 256 bytes?**  
Porque usamos RSA de 2048 bits, y 2048 ÷ 8 = 256 bytes. El tamaño de la firma depende del tamaño de la llave, no del documento.

**¿Debo guardar la llave privada?**  
Depende. Si no la guardas, cada vez que firmes se genera una llave nueva y la llave pública anterior queda inútil. Si la guardas, puedes firmar múltiples documentos y cualquiera puede verificarlos con la misma llave pública.

---

## Equivalencias con Java (guía Oracle)

| Java | Python |
|---|---|
| `KeyPairGenerator.getInstance("DSA")` | `rsa.generate_private_key()` |
| `Signature.getInstance("SHA1withDSA")` | RSA-PSS con SHA-256 (más moderno) |
| `X509EncodedKeySpec` | `PublicFormat.SubjectPublicKeyInfo` (mismo estándar X.509) |
| `sig.sign()` | `private_key.sign()` |
| `sig.verify()` | `public_key.verify()` |

> **Nota:** Se usó RSA en lugar de DSA y SHA-256 en lugar de SHA-1 porque son los estándares actuales más seguros. El concepto y el flujo son idénticos.

---

## Limitación conocida

Este sistema no incluye **certificados digitales**. Eso significa que si alguien genera su propio par de llaves y te manda su `public_key.pem` haciéndose pasar por otra persona, no hay forma de saberlo. En sistemas reales esto se resuelve con autoridades certificadoras (CA) que firman y validan las llaves públicas — es el siguiente nivel de seguridad.

---

## Versiones

| Versión | Descripción |
|---|---|
| `v1.0` — CLI | Implementación por línea de comandos (`GenSig.py` + `VerSig.py`) |
| `v2.0` — GUI | Se agrega `app_firma.py` como interfaz gráfica. `GenSig.py` y `VerSig.py` se refactorizan para ser importables como módulos sin romper su funcionamiento CLI |