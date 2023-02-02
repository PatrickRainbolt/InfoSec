#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# Diffie-Hellman is to demostrate how share key cipher works.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import textwrap
import random

def BitRandom(num):
    return(random.randrange(2**(num-1)+1, 2**num-1))

def getPrime(num): 
    while True:
        tempPrime = BitRandom(num)
        if tempPrime % 2 != 0:
            break    
    return tempPrime

def fixedOutput(fpre , fvalue):
    prefix = fpre + ": "
    prefix = ' '*(20 - len(prefix)) + prefix
    preferredWidth = 100
    wrapper = textwrap.TextWrapper(initial_indent=prefix, width=preferredWidth,
                                   subsequent_indent=' '*len(prefix))
    print(wrapper.fill(str(fvalue)))
    print("\n")

termColorYellow = '\033[93m'
termColorEnd = '\033[0m'

print("-----------------------------------------------------------")
print("- Setting up the primary Program Prime and Primitive Root -")
print("-----------------------------------------------------------\n")

prime = getPrime(1024)
fixedOutput("The Program Prime", prime)

root = getPrime(1024)
fixedOutput("The Primitive Root", root)


print("-----------------------------------------------------------")
print("- Alice and Bob create their Private keys                 -")
print("-----------------------------------------------------------\n")

AlicePrivateKey = getPrime(1024)
fixedOutput("Alice Private Key", AlicePrivateKey)

BobPrivateKey = getPrime(1024)
fixedOutput("Bob Private Key", BobPrivateKey)

print("-----------------------------------------------------------")
print("- Alice and Bob create their Public keys                  -")
print("-----------------------------------------------------------\n")

AlicePublicKey = pow(root, AlicePrivateKey, prime)
print("Alice calculates her public key: " + termColorYellow + 
	" AlicePublicKey = root ^ AlicePrivateKey mod Prime " + termColorEnd + ":")
fixedOutput("AlicePublicKey", AlicePublicKey)

BobPublicKey = pow(root, BobPrivateKey, prime)
print("Bob calculates his public key:  " + termColorYellow + 
	" BobPublicKey = root ^ BobPrivateKey mod prime " + termColorEnd + ":")
fixedOutput("BobPublicKey", BobPublicKey)

print("-----------------------------------------------------------")
print("- How to calculate the Password from their Private Keys   -")
print("-----------------------------------------------------------\n")

AliceKey = pow(BobPublicKey, AlicePrivateKey, prime)
print("Alice calculates the shared key as " + termColorYellow + 
	"Key = BobPublicKey ^ AlicePrivateKey mod prime " + termColorEnd + ":")
fixedOutput("AliceKey", AliceKey)

BobKey = pow(AlicePublicKey, BobPrivateKey, prime)
print("Bob calculates the shared key as " + termColorYellow + 
	"Key = ALicePublicKey ^ BobPrivateKey mod prime " + termColorEnd + ":")
fixedOutput("BobKey", BobKey)

print("\n\n")
