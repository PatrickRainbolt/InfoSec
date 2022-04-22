#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# Diffie-Hellman is to demostrate how share key cipher works.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import random
global prime, root

def BitRandom(num):
    return(random.randrange(2**(num-1)+1, 2**num-1))

def getPrime(num): 
    while True:
        tempPrime = BitRandom(num)
        if tempPrime % 2 != 0:
            break    
    return tempPrime

prime = getPrime(256)
print("The Program Prime:---[",prime, "]")

# root = secretnumber(5, 10)
root = getPrime(10)
print("The Primitive Root:--[",root, "]\n")

#alicesecret = secretnumber(100, 1000)
AlicePrivateKey = getPrime(10)
print("Alice Private Key:---[",AlicePrivateKey, "]")

#bobsecret = secretnumber(000, 1000)
BobPrivateKey = getPrime(10)
print("Bob Private Key:-----[", BobPrivateKey, "]\n")

AlicePublicKey = (root ** AlicePrivateKey) % prime
print("Alice calculates her public key:  AlicePublicKey = root ^ AlicePrivateKey mod Prime :")
print("-[",AlicePublicKey, "]\n")

BobPublicKey = (root ** BobPrivateKey) % prime
print("Bob calculates his public key:    BobPublicKey = root ^ BobPrivateKey mod prime :")
print("-[", BobPublicKey, "]\n\n\n\n")

print("*** How to calculate the Password from their keys ***\n")

AliceKey = (BobPublicKey ** AlicePrivateKey) % prime
print("Alice calculates the shared key as Key = BobPublicKey ^ AlicePrivateKey mod prime :")
print("-[", AliceKey, "]\n")

BobKey = (AlicePublicKey ** BobPrivateKey) % prime
print("Bob calculates the shared key as Key = ALicePublicKey ^ BobPrivateKey mod prime :")
print("-[", BobKey, "]\n\n")
