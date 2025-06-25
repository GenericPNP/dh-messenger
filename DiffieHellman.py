import random
class DiffieHelman:
    def __init__(self, prime, modulus):
        self.prime = prime #large prime number
        self.modulus = modulus #root modulo prime
        self.privKey = random.randint(1, self.prime - 1) #priv key between 1 and prime-1
        self.pubKey = self.calcPubKey() #pub key

    def calcPubKey(self):
        #'modulus' ^ 'privKey'
        exp = pow(self.modulus, self.privKey)
        #'exp' mod 'prime'
        mod = exp % self.prime
        return mod
    
    def calcSharedSecret(self, otherKey):
        #'otherKey' ^ 'privKey'
        exp = pow(otherKey, self.privKey)
         #'exp' ^ 'prime'
        mod = exp % self.prime
        return mod
    