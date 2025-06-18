# AES-BASED-LSB-STEGANOGRAPHY
A Python project that implements Least Significant Bit (LSB) steganography for hiding encrypted messages inside RGB images. This tool allows you to securely hide binary data, such as AES-encrypted messages, inside image files without altering their visible appearance.

📌 Features
✅ AES Encryption/Decryption (Optional, if used with an AES module)

🖼️ Steganographic Encoding using Least Significant Bits

🔍 Decoding and Extraction of hidden data

📦 Works with standard RGB images (e.g., .bmp, .png)

🔐 Suitable for hiding text, passwords, or binary data securely

🧪 Simple and modular code for easy customization

🧠 How It Works
Encoding:
Each byte of the message is converted into an 8-bit binary string.

All binary bits are concatenated into a single long bitstream.

The first 24 bits of the image (8 pixels × 3 channels) are reserved to store the message length.

Remaining bits are embedded into the least significant bits (LSBs) of each RGB pixel channel.

The modified image is saved with a _hidden.bmp suffix.

Decoding:
The first 24 LSBs of the image are extracted to get the original message length.

The following bits are read from the LSBs of the pixels.

The binary stream is reconstructed into a list of bytes (integers).

The output can be decrypted if previously encrypted.

🚧 Limitations
Cannot hide large messages in small images (due to space constraints).

No error detection/correction — assumes a clean image.

No support for lossy formats like JPEG (will corrupt hidden data).

📚 Dependencies
Python 3.x

Pillow (pip install Pillow)

If using encryption:

Custom aes.py module implementing AES encryption (you can also use pycryptodome or cryptography).
