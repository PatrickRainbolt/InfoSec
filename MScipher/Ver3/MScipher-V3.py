#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# MScipher is a Shift Cipher but every character has a unique shift table. This is accomplished by
#    adding in a Rotation key or Password to the Cipher.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import sys
import signal
import re
import random
import os

# Setting this to True will show all Debug messages
Debug = False

# Setting this to True will take any charater not in the List to be reprinted normally.
WordSkip = True

# Storage Variable for for Word List.
WordList = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Storage Variable for intial Shift value.
Shift = 5

# Storage Variable for Rotater Keys / Password values.
Rotate = []

# Setting this to True wil request a password to be entered.
PassSet = False

# Storage Variable for coding password.
Password = 'SECRET'

# File location and name to output text data
Outfile = ""

# Setting this to True will only increment rotation on a valid charater in the List.
Leap = False

# Storage Variable to show what direction Shift is Justified
Justify = "Left"

# File location and name to input text data
Infile = ""

# Setting this to True will Decipher the message
DeCipher = False

# Setting this to True converts all character to uppercase before processing.
Convert = False

# Default Keys Prime Value: This constant will change any public or decipher values if changed.
prime = 98348149859422759653449222024902527358447401882717513832658752589732178323087

# Default Keys Primitive Root: This constant will change any public or decipher values if changed.
root = 112610998970462321170418252784376929165518212068608580368800985994928452406337

# Default Keys Folder Location: Modify this to your home folder.
DefaultKeyFolder = os.environ['HOME'] + "/.MScipher"

# Setting this to True will use Diffie-Hellman keys instead of a Passcode.
KeyPair = False

# Diffie-Hellman username in the Public Key Ring
KeyPairName = ""


# Syntax Information
def SyntaxInformation():
     print("""SYNTAX: MScipher <args> <passcode> <text>

     {-s} or {--shift}     Sets MScipher shift value.
     {-d} or {--decipher}  Puts MScipher into a Decipher Mode.
     {-j} or {--justify}   Sets MScipher into what Method to Shift Key List,
                              Followed by {"Left"/"Mid"/"Right"} Left and Right ar both 
                              explainitary. Mid looks at the Rotate bit and shift Left
                              if less than or equal to the mid point of the Key List size.
     {-l} or {--leap}      Sets MScipher to Only Increment the next Rotation
     {-k} of {--keypair}   This will cause the program to use Rotator Key Pairs for the cipher. 
     {-p} or {--password}  Ask for the Rotate Key or Password after running.
     {-u} or {--upper}     Sets MScipher to Uppercase all Alphabetic Characters.

     {--minimal}    Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789} This is the Default.
     {--standard}   Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789}
     {--enlarged}   Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz}
     {--expanded}   Sets Key to {AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 0123456789}

     {--keyroot}    Generates a new set of Rotator Keys Prime Value and Keys Primitive Root.
     {--keygen}     This will cause the program to generate Rotator Key Pairs. 
                              value on a valid charater in the List.
     {--keypub}     Outputs the current Public Rotator Key to Share with others.
     {--keylist}    List the contents of your Public Key Ring.
     {--keyadd}     Adds an entry from your Public Key Ring.
     {--keydel}     Deletes an entry from your Public Key Ring.
     {--debug}      Turns on verbose mode.
     """)
     sys.exit()


# Command Line Parser
def CmdLineParser():
     global Debug
     global Convert
     global DeCipher
     global Infile
     global Justify
     global KeyPair
     global KeyPairName
     global Leap
     global Outfile
     global PassSet
     global Password
     global Shift
     global WordList
     inData = ''

     if len(sys.argv) < 2:
         SyntaxInformation()
     ARG = sys.argv
     DebugOut = "\nMScipher Debug-Mode Active:\n# ARGS[" + str(len(ARG)).rjust(2, ' ') + "]  ARG"+str(ARG[1:])+"\n\n"

     while len(ARG) > 1:
         # Checking for any multiple case arguments.
         if ARG[1][0] == "-" and ARG[1][1] != "-" and len(ARG[1]) > 2:
             # Splits out all multiple case arguments into seperate arguments.
             for Char in ARG[1][::-1]:
                  if Char != "-":
                      ARG.insert(2,"-"+Char)
             del ARG[1]

         DebugOut += "- ARGS[" + str(len(ARG)).rjust(2, ' ') + "]  ARG["+str(ARG[1])+"]"
         if ARG[1].lower() == "--debug":                                   # Turn on Debug Mode
             Debug = True
         elif ARG[1].lower() == "-d" or ARG[1].lower() == "--decipher":    # Sets MScipher into Decrypt Mode
             DeCipher = True
         elif ARG[1].lower() == "-j" or ARG[1].lower() == "--justify":     # Sets what Direction to Shift
             if len(ARG) > 1:
                 if ARG[2] == "Left": Justify = "Left"
                 elif ARG[2] == "Right": Justify = "Right"
                 else: Justify = "Mid"
                 DebugOut += " + ["+str(ARG[2])+"]"
                 del ARG[2]
         elif ARG[1].lower() == "-l" or ARG[1].lower() == "--leap":        # Only increment rotation on a valid charater in the List
             Leap = True
         elif ARG[1].lower() == "-p" or ARG[1].lower() == "--password":    # Turn on Request Password
             PassSet = True
         elif ARG[1] == "--minimal":                                       # Sets Minimal Key List
             WordList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
         elif ARG[1] == "--standard":                                      # Sets Standard Key List
             WordList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"
         elif ARG[1] == "--enlarged":                                      # Sets Enlarged Key List
             WordList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
         elif ARG[1] == "--expanded":                                      # Sets Expanded Key List
             WordList = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 0123456789"
         elif  ARG[1] == "-s" or ARG[1].lower() == "--shift":              # Set Shift Value
             if len(ARG) > 1:                                              # Confirming Next Value is Int and storing.
                 tmpShift = re.compile(r'[^\d.]+')
                 if tmpShift.sub('',ARG[2]) != '':
                     Shift = int(tmpShift.sub('',ARG[2]))
                     DebugOut += " + ["+str(ARG[2])+"]"
                     del ARG[2]
         elif ARG[1].lower() == "-u" or ARG[1].lower() == "--upper":        # Turn on Request Password
             Convert = True
         elif ARG[1].lower() == "-k" or ARG[1].lower() == "--keypair":      # Sets cipher to use KeyPair instead of Password.
             if len(ARG) > 2:
                 KeyPairName = str(ARG[2]) 
                 KeyPair = True
                 DebugOut += " + ["+str(ARG[2])+"]"
                 del ARG[2]
         elif ARG[1].lower() == "--keygen": generateNewKeys()               # Will generate and store Rotator Key Pairs.
         elif ARG[1].lower() == "--keyroot": generateRoot()                 # Will generate new Keys Prime Value and Keys Primitive Root.
         elif ARG[1].lower() == "--keypublic": showPublicKey()              # Will display your current Public Key.
         elif ARG[1].lower() == "--keylist": showPublicKeyRing()            # Will display your current Public Key Ring.
         elif ARG[1].lower() == "--keyadd":                                 # Will add a key to your Public Keys Ring.
             if len(ARG) > 2:
                 addPublicKeyRing(str(ARG[2]))
             else:
                 print("SYNTAX: MScipher --keyadd <user_name>")
             sys.exit()
         elif ARG[1].lower() == "--keydel":                                 # Will del a key to your Public Keys Ring.
             if len(ARG) > 2:
                 delPublicKeyRing(str(ARG[2]))
             else:
                 print("SYNTAX: MScipher --keydel <user_name>")
             sys.exit()
         elif ARG[1][0] != "-": inData = ARG[1]
         del ARG[1]
         DebugOut += "\n"

     if inData == "":
         # No Text was found in the Arguments, checking STDIN for Text,
         if not sys.stdin.isatty():
             inData = sys.stdin.read()[:-1]
             DebugOut += "-  STD[--]   IN["+str(inData)+"]\n"
         if inData == "": 
             SyntaxInformation()

     if Debug: print(DebugOut)
     if PassSet: Password = input('Please Enter a Password for Ciphering:')
     if Debug:
         print("- LEN[" + str(len(WordList)).rjust(2, ' ') + "] LST["+ WordList +"]")
         if not KeyPair: print("- LEN[" + str(len(Password)).rjust(2, ' ') + "] PAS["+ Password +"]")
     return inData

# Put in place to handle CTRL-C being pressed.
def handler(signum, frame):
     print(" ")
     exit(1)


# Code by tabmir at https://www.geeksforgeeks.org/how-to-generate-large-prime-numbers-for-rsa-algorithm/
#    I have included these Prime generating routines to speed up programs run time. 
#-----------------------------------------------------------------------------------------------------------
first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
   73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
   179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 
   281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349]
def nBitRandom(n): return random.randrange(2**(n-1)+1, 2**n - 1)
def getLowLevelPrime(n):
    while True:
        pc = nBitRandom(n)
        for divisor in first_primes_list:
            if pc % divisor == 0 and divisor**2 <= pc: break
            else: return pc
def isMillerRabinPassed(mrc):
    maxDivisionsByTwo = 0; ec = mrc-1
    while ec % 2 == 0:
        ec >>= 1; maxDivisionsByTwo += 1
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
#-----------------------------------------------------------------------------------------End code by tabmir

# Rotator Key Pairs: Outputs the current Public Rotator Key.
def showPublicKey():
    if not os.path.exists(DefaultKeyFolder + "/MSc.pub"): print("MScipher: No Public key was found!\n")
    else: 
         f = open(DefaultKeyFolder + "/MSc.pub", "r")
         PubKey = f.read()
         f.close()
         sys.stdout.write(PubKey)
    sys.exit()

# Rotator Key Pairs: Show all public keys in the Key Ring.
def showPublicKeyRing():
    if not os.path.exists(DefaultKeyFolder + "/MSc.keys"): print("MScipher: Can not locate Public Key Ring!\n")
    else: 
         f = open(DefaultKeyFolder + "/MSc.keys", "r")
         PubKey = f.read()
         f.close()
         sys.stdout.write(PubKey)
    sys.exit()

# Rotator Key Pairs: Generates a new Rotator Public and Private key pair.
def generateNewKeys():
    SanityCheck = input("Are you sure you want to generate Rotator Key Pairs, This will overwrite any other Keys (Yes or No): ")
    if SanityCheck.lower() != "yes": sys.exit()
    Password = input("\n\nPlease Enter a Key Password: ")

    print("\nGenerating Rotator Key Pairs:")
    WordList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    Shift = CreateShift(5, WordList, False)
    Cipher = Ceasar(Shift, "Mid", WordList, False); LenCipher = len(Cipher)
    Rotate = CreateRotators(Cipher, Password, True, False)
    passRoot = int("".join(map(str, Rotate)))

    print("- Public and Private Keys have been generated.")
    PrivateKey = getPrime(14)
    SecureKey = PrivateKey + passRoot
    PublicKey = PublicKey = (root ** PrivateKey) % prime
    Keys = [ "MSprv:"+str(SecureKey), "MSpub:"+str(PublicKey) ]

    # Saving Keys to filesystem
    if not os.path.exists(DefaultKeyFolder): os.makedirs(DefaultKeyFolder)
    if not os.path.exists(DefaultKeyFolder + "/MSc.pub"): f = open(DefaultKeyFolder + "/MSc.pub", "x")
    else: f = open(DefaultKeyFolder + "/MSc.pub", "w")
    f.write(Keys[1] + "\n"); f.close()
    if not os.path.exists(DefaultKeyFolder + "/MSc.prv"): f = open(DefaultKeyFolder + "/MSc.prv", "x")
    else: f = open(DefaultKeyFolder + "/MSc.prv", "w")
    f.write(Keys[0] + "\n"); f.close()
    if not os.path.exists(DefaultKeyFolder + "/MSc.keys"): 
        f = open(DefaultKeyFolder + "/MSc.keys", "x")
        f.write("MScipher Public Key Ring Storage File.\n" +
                "----------------------------------------------------------------------------------------------\n")
        f.close()
    print("- Rotator Key Pairs have been generated and stored.\n\nTo view your Public Key: MScipher --keypublic\n")
    sys.exit()

# Rotator Key Pairs: Add a person Public Key to the Rotator Key Ring.
def addPublicKeyRing(inName):
     if inName == "":
          print("SYNTAX: MScipher --keyadd <user_name>")
          sys.exit()
     inPublicKey = input("\nEnter Public Key for " + inName + ": ")
     if not os.path.exists(DefaultKeyFolder + "/MSc.keys"): 
         f = open(DefaultKeyFolder + "/MSc.keys", "x")
         f.write("MScipher Public Key Ring Storage File.\n" +
                "----------------------------------------------------------------------------------------------\n")
     else: f = open(DefaultKeyFolder + "/MSc.keys", "a")
     f.write(inName + ":" + inPublicKey + "\n")
     f.close()
     print("\nMScipher:",inName, "was added to the Rotator Key Ring.")
     sys.exit()

# Rotator Key Pairs: Deletes a person Public Key to the Rotator Key Ring.
def delPublicKeyRing(inName):
    if not os.path.exists(DefaultKeyFolder + "/MSc.keys"): print("\nMScipher: Can not locate Public Key Ring!\n")
    else: 
         KeyFound = False
         f = open(DefaultKeyFolder + "/MSc.keys", "r")
         Keys = f.readlines()
         f.close()
         f = open(DefaultKeyFolder + "/MSc.keys", "w")
         for Key in Keys:
              if not Key[:len(inName)] == inName:
                   f.write(Key)
              else: KeyFound = True
         f.close()
         if not KeyFound: print("\nMScipher:",inName, "was not locate in the Public Key Ring!\n")
         else: print("\nMScipher:",inName, "was delted from your Public Key Ring!\n")
    sys.exit()

# Rotator Key Pairs: Generate new Keys Prime Value and Keys Primitive Root.
def generateRoot():
    print(" The Program Prime:",getPrime(256))
    print("The Primitive Root:",getPrime(256), "\n")
    print("NOTE: Copy and Paste these values into the default variables. Warning changing these variable\n" + 
        "  will require new public keys and will not decode privious messages that used the old Key pairs.\n" +
        "  Anyone you are communicating with will also have to change their values to match these new Key pairs.") 
    sys.exit()


# Checking if Shift is larger than the WordLst length. If so it does a Modular to
#   length to get Shift Value.
def CreateShift(inShift, inList, inDebug):
     if inShift >= len(inList):
         if inDebug: print("- LEN[->] pSHF["+str(inShift)+"] MOD["+str(inShift) + "-INT("+str(inShift) + "/" + 
             str(len(inList)) + ")] SHF[" + str(inShift % len(inList)) + "]")
         inShift = inShift % len(inList)
     else:
         if inDebug: print("- LEN[..] SHF["+str(inShift)+"]\n")
     return inShift

# Creating Shifted Set (Values are: Left, Mid, Right)
def Ceasar(inShift, inDir , inLst, inDebug):
     if inDir == 'Mid':
         if inShift < int(len(WordList) / 2): inDir = 'Left'
         else: inDir = 'Right'
     if inDir == 'Right': inShift *= -1
     if inDebug: print("- " + inDir[0], end ="")
     return inLst[inShift:] + inLst[:inShift]

# Getting Rotate Values from Password using Intial Shifted List.
def CreateRotators(inCipher, inPass, inConvert, inDebug):
     tmpRotate = []
     if inDebug: print("\n- LEN[" + str(len(inCipher)).rjust(2, ' ') + "] LST["+ inCipher +"]")

     if inConvert: inPass = inPass.upper()
     for char in inPass:
         if Convert: tmpRotate.append(inCipher.find(char.upper()))
         else: tmpRotate.append(inCipher.find(char))

         if inDebug: print("# CHAR[" + str(char) +"] POS[" + str(tmpRotate[-1]).rjust(2, ' ') + "]")
     if inDebug: print("- LEN[" + str(len(tmpRotate)).rjust(2, ' ') + "] ROT" + str(tmpRotate)+"\n")
     return tmpRotate

# Rotator Key Pairs: Converts Public
def KeyRotators(inWordList, inKey, inDebug):
     ListLength = len(inWordList)
     Rotate = [int(str(inKey)[i:i+2]) for i in range(0, len(str(inKey)), 2)]
     loop = 0
     while loop < len(Rotate):
          if Rotate[loop] > ListLength:
               if Rotate[loop] > 9: Rotate[loop] = int(str(Rotate[loop])[0]) + int(str(Rotate[loop])[1])
               if Rotate[loop] > ListLength: Rotate[loop] = Rotate[loop] % ListLength
          loop = loop + 1
     if inDebug: print("- LEN[" + str(len(Rotate)).rjust(2, ' ') + "] ROT" + str(Rotate)+"\n")
     return Rotate

# Rotator Key Pairs: Using Private and a Public key to generate Rotators
def CreateCipherKey(inName, inDebug):
     if inDebug: print("- Loading Public Key for", inName, end="")
     if not os.path.exists(DefaultKeyFolder + "/MSc.keys"): 
          print("\nMScipher: Can not locate Public Key Ring!\n")
          sys.exit()
     else: 
          KeyFound = False
          f = open(DefaultKeyFolder + "/MSc.keys", "r")
          Keys = f.readlines()
          f.close()
          for Key in Keys:
               if Key[:len(inName)] == inName:
                   UserPublicKey = int(Key[len(inName)+1:-1])
                   KeyFound = True 
          if not KeyFound: 
               print("\nMScipher:",inName, "was not locate in the Public Key Ring!\n")
               sys.exit()
     if inDebug: print(" ["+str(UserPublicKey)+"]")

     if inDebug: print("- Loading Your Private Key.")
     if not os.path.exists(DefaultKeyFolder + "/MSc.prv"): print("\nMScipher: Can not locate your Private Key!\n")
     else: 
          f = open(DefaultKeyFolder + "/MSc.prv", "r")
          PrivateKey = f.read()
          f.close()
     PrivateKey = int(PrivateKey[6:])
     inPasswd = input("Please Enter your Key Ring Password: ")
     if inDebug: print("- Deciphering Private Key.\n")
     WordList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
     Shift = CreateShift(5, WordList, False); 
     Cipher = Ceasar(Shift, "Mid", WordList, False); LenCipher = len(Cipher)
     Rotate = CreateRotators(Cipher, inPasswd, True, False)
     passRoot = int("".join(map(str, Rotate)))
     PrivateKey = PrivateKey - passRoot
     if len(str(PrivateKey)) > 6:
          print("\nMScipher: Invalid Private Key Password!\n")
          sys.exit()
     return (UserPublicKey ** PrivateKey) % prime

# Encript Text string with rotate keys.
def Encrypt(inShift, inJustify, inRotate, inWordList, inText, inConvert, inLeap, inDebug):
     CipherText = ""
     lpRotate = 0
     LenWordList = len(inWordList)

     if inConvert: inWordList = inWordList.upper()
     for inChar in inText:
         if (inLeap and inConvert and inWordList.find(inChar.upper()) == -1) or (inLeap and inConvert == False and inWordList.find(inChar) == -1):
             EncodedChar = inChar
             if inDebug: print("- S[" + inChar + "] pSHF[--] ROT[--] " + ("-"*len(ShiftLst)) + " SFT[--] POS[--] = [" + EncodedChar + "]")
         else:
             # Gets Shift + Rotate Vaule, if larger than List it subtracts List Length from Shift.
             preShift = inShift
             inShift = inShift + inRotate[lpRotate]
             if inShift > LenWordList: inShift -= LenWordList
             # Converts all letters to uppercase and finds character position
             if inConvert: PosChar = inWordList.find(inChar.upper())
             else: PosChar = inWordList.find(inChar)

             # Creates new list for new Shift position
             ShiftLst = Ceasar(inShift, inJustify, inWordList, inDebug)
             # Grabs character from new list using found position.
             if PosChar != -1: EncodedChar = ShiftLst[PosChar]
             else: EncodedChar = inChar
             if inDebug: print("[" + inChar + "] pSHF["+str(preShift).rjust(2, ' ')+"] ROT["+str(inRotate[lpRotate]).rjust(2, ' ')+"] " + 
                 ShiftLst + " SFT["+ str(inShift).rjust(2, ' ') + "] POS["+ str(PosChar).rjust(2, ' ') + "] = [" + EncodedChar + "]")
             # Checks to see that we have not used all the Rotate Values, if so it starts over.
             if lpRotate == len(inRotate) - 1:
                 lpRotate = 0
             else:
                 lpRotate += 1
         # Appends new character to Ciphered Text
         CipherText += EncodedChar

     if inDebug:
         print(" ")
         print("- PlainText: " + inText)
         print("- Encrypted: " + CipherText)
         print(" ")
     return CipherText

# Decript Cripted string with rotate keys.
def Decrypt(inShift, inJustify, inRotate, inWordList, inText, inConvert, inLeap, inDebug):
     PlainText = ""
     lpRotate = 0
     LenWordList = len(inWordList)

     if inConvert: inWordList = inWordList.upper()
     for inChar in inText:
         if (inLeap and inConvert and inWordList.find(inChar.upper()) == -1) or (inLeap and inConvert == False and inWordList.find(inChar) == -1):
             DecodedChar = inChar
             if inDebug: print("- S[" + inChar + "] pSHF[--] ROT[--] " + ("-"*len(ShiftLst)) + " SFT[--] POS[--] = [" + DecodedChar + "]")
         else:
             preShift = inShift
             # Gets Shift + Rotate Vaule, if larger than List it subtracts List Length from Shift.
             inShift = inShift + inRotate[lpRotate]
             if inShift > LenWordList: inShift -= LenWordList

             # Creates new list for new Shift position
             ShiftLst = Ceasar(inShift, inJustify ,inWordList, inDebug)
             # Converts all letters to uppercase and finds character position
             if inConvert: PosChar = ShiftLst.find(inChar.upper())
             else: PosChar = ShiftLst.find(inChar)

             # Grabs character from new list using found position.
             if PosChar != -1: DecodedChar = inWordList[PosChar]
             else: DecodedChar = inChar
             if inDebug: print("[" + inChar + "] pSHF["+str(preShift).rjust(2, ' ')+"] ROT["+str(inRotate[lpRotate]).rjust(2, ' ')+"] " + 
                 ShiftLst + " SFT["+ str(inShift).rjust(2, ' ') + "] POS["+ str(PosChar).rjust(2, ' ') + "] = [" + DecodedChar + "]")

             # Checks to see that we have not used all the Rotate Values, if so it starts over.
             if lpRotate == len(inRotate) - 1:
                 lpRotate = 0
             else:
                 lpRotate += 1
         # Appends new character to Ciphered Text
         PlainText += DecodedChar

     if inDebug:
         print(" ")
         print("- Encrypted: " + inText)
         print("- PlainText: " + PlainText)
         print(" ")
     return PlainText


# Main Routines
signal.signal(signal.SIGINT, handler)
CmdText = CmdLineParser()
if Infile != "":
    print("ready!")

if CmdText == "":
    print("No Data Provided...")

Shift = CreateShift(Shift, WordList, Debug)
Cipher = Ceasar(Shift, Justify, WordList, False)
LenCipher = len(Cipher)

if KeyPair: Rotate = KeyRotators("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", CreateCipherKey(KeyPairName, Debug), Debug)
else: Rotate = CreateRotators(Cipher, Password, Convert, Debug)


if DeCipher: outText = Decrypt(Shift, Justify, Rotate, WordList, CmdText, Convert, Leap, Debug)
else: outText = Encrypt(Shift, Justify, Rotate, WordList, CmdText, Convert, Leap, Debug)

sys.stdout.write(outText)
print("")
