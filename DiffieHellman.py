import random
class DiffieHellman:
    def __init__(self, prime, base):
        self.prime = prime #large prime number
        self.base = base #root modulo prime
        self.privKey = random.randint(1, self.prime - 1) #Each part generates a random private key
        self.pubKey = self.calcPubKey() #Each party generates a public key based on their private key

    def calcPubKey(self):
       return pow(self.base, self.privKey, self.prime) #Function to compute the public key
    
    def calcSharedSecret(self, otherKey):
        return pow(otherKey, self.privKey, self.prime) # Compute the shared secret


def key_to_string(key):
    return str(key).encode('utf-8').hex() # Convert the number to a string, Encode that string into bytes, convert the bytes into hex



    
