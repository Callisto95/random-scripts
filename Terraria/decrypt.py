from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os


def decrypt_file(input_file, output_file):
    try:
        # Equivalent to C# UnicodeEncoding (UTF-16LE)
        key_string = "h3y_gUyZ"
        key = key_string.encode("utf-16le")

        # RijndaelManaged defaults:
        # BlockSize = 128
        # Mode = CBC
        # Padding = PKCS7
        cipher = AES.new(key, AES.MODE_CBC, key)

        with open(input_file, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        # Remove PKCS7 padding (same as .NET default)
        decrypted_data = unpad(decrypted_data, AES.block_size)

        with open(output_file, "wb") as f:
            f.write(decrypted_data)

        return False  # matches C# return on success

    except Exception:
        if os.path.exists(output_file):
            os.remove(output_file)
        return True  # matches C# return on failure


if __name__ == "__main__":
    print(decrypt_file("Calli.plr", "decrypt.plr"))
