#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# Diffie-Hellman is to demostrate how share key cipher works.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import random
global prime, root


# Code by tabmir at https://www.geeksforgeeks.org/how-to-generate-large-prime-numbers-for-rsa-algorithm/
#-----------------------------------------------------------------------------------------------------------

# Pre generated primes
first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 
                     89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 
                     181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 
                     277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349]

def nBitRandom(n):
    return random.randrange(2**(n-1)+1, 2**n - 1)
 
def getLowLevelPrime(n):
    while True:
        pc = nBitRandom(n)
        for divisor in first_primes_list:
            if pc % divisor == 0 and divisor**2 <= pc: break
        else: return pc
 
def isMillerRabinPassed(mrc):
    maxDivisionsByTwo = 0
    ec = mrc-1
    while ec % 2 == 0:
        ec >>= 1
        maxDivisionsByTwo += 1
    assert(2**maxDivisionsByTwo * ec == mrc-1)
 
    def trialComposite(round_tester):
        if pow(round_tester, ec, mrc) == 1: return False
        for i in range(maxDivisionsByTwo):
            if pow(round_tester, 2**i * ec, mrc) == mrc-1: return False
        return True
 
    numberOfRabinTrials = 20
    for i in range(numberOfRabinTrials):
        round_tester = random.randrange(2, mrc)
        if trialComposite(round_tester): return False
    return True

def getPrime(num):
    while True:
        prime_candidate = getLowLevelPrime(num)
        if not isMillerRabinPassed(prime_candidate): continue
        else: return prime_candidate
#-----------------------------------------------------------------------------------------------------------


prime = getPrime(256)
print("The Program Prime---[",prime, "]")

root = getPrime(256)
print("The Primitive Root--[",root, "]\n")

AlicePrivateKey = getPrime(14)
print("Alice Private Key--[",AlicePrivateKey, "]")

BobPrivateKey = getPrime(14)
print("Bob Private Key--[", BobPrivateKey, "]\n")

print("Alice calculates her public key:  AlicePublicKey = root ^ AlicePrivateKey mod Prime :")
AlicePublicKey = (root ** AlicePrivateKey) % prime
print("--[",AlicePublicKey, "]\n")

print("Bob calculates his public key:    BobPublicKey = root ^ BobPrivateKey mod prime :")
BobPublicKey = (root ** BobPrivateKey) % prime
print("--[", BobPublicKey, "]\n\n\n\n")

print("*** How to calculate the Password from their keys ***\n")

AliceKey = (BobPublicKey ** AlicePrivateKey) % prime
print("Alice calculates the shared key as Key = BobPublicKey ^ AlicePrivateKey mod prime :")
print("--[", AliceKey, "]\n")

BobKey = (AlicePublicKey ** BobPrivateKey) % prime
print("Bob calculates the shared key as Key = ALicePublicKey ^ BobPrivateKey mod prime :")
print("--[", BobKey, "]\n\n")

