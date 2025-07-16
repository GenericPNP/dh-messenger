# Ensures that only printable ASCII characters are used
PRINTABLE_START = 32
PRINTABLE_END = 126
PRINTABLE_RANGE = PRINTABLE_END - PRINTABLE_START + 1

class Vigenere:
    @staticmethod
    def vigenere_encrypt(plaintext, key):
        key = key * ((len(plaintext) // len(key)) + 1)  # Extend key to match length of plaintext
        ciphertext = ""
        for p, k in zip(plaintext, key):
            shifted = ((ord(p) - PRINTABLE_START) + (ord(k) - PRINTABLE_START)) % PRINTABLE_RANGE
            ciphertext += chr(shifted + PRINTABLE_START)
        return ciphertext

    @staticmethod
    def vigenere_decrypt(ciphertext, key):
        key = key * ((len(ciphertext) // len(key)) + 1)  # Extend key to match length of ciphertext
        plaintext = ""
        for c, k in zip(ciphertext, key):
            shifted = ((ord(c) - PRINTABLE_START) - (ord(k) - PRINTABLE_START)) % PRINTABLE_RANGE
            plaintext += chr(shifted + PRINTABLE_START)
        return plaintext
