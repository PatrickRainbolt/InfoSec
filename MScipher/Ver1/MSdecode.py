#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# MSdecode is a Shift Cipher but every character has a unique shift table. This is accomplished by 
#    adding in a Rotation key or Password to the Cipher.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import sys

# Shows Debug Information.
Debug = True
# Default Word List.
WordLst = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"

# Creating Shifted Set
def Ceasar(inShift , inLst):
     return inLst[inShift:] + inLst[:inShift] 


# Just something simple for testing my ideas.
if len(sys.argv) < 4:
    print("SYNTAX: MSencode <Shift_Value> <Password> <Text_To_Encode>")
    exit()
Shift = int(sys.argv[1])
PassWord = sys.argv[2]
inText = sys.argv[3]

# Checking if Shift is larger than the WordLst length. If so it does a Modular to 
#   length to get Shift Value.
if Shift >= len(WordLst):
    Shift = Shift % len(WordLst)

# Creating intial Shifted List 
Cipher = Ceasar(Shift, WordLst) 
LenCipher = len(Cipher)
if Debug:
    print("]-[ ....-....+....-....+....-....+....-....+....-....+....-....+....-....+")
    print("]-[ " + WordLst + "  --LEN[" + str(len(WordLst)) + "]")
    print("]-[ " + Cipher + "  --SHIFT[" + str(Shift) + "]")
    print(" ")

# Getting Rotate Values from Password using Intial Shifted List.
Rotate = []
for char in PassWord:
    Rotate.append(Cipher.find(char.upper()))
if Debug:
    print("]-[ Rotators" + str(Rotate))
    print(" ")
    print("]-[ ....-....+....-....+....-....+....-....+....-....+....-....+....-....+")

# Parsing InText data and creating Cipher Text
PlainText = ""
Rotator = 0
for inChar in inText:
    # Gets Shift + Rotate Vaule, if larger than List it subtracts List Length from Shift.
    Shift = Shift + Rotate[Rotator]
    if Shift > LenCipher:
        Shift -= LenCipher
    
    # Creates new list for new Shift position
    ShiftLst = Ceasar(Shift, WordLst)
    # Converts all letters to uppercase and finds character position
    PosChar = ShiftLst.find(inChar.upper())

    # Grabs character from original Word list using found position.
    DecodedChar = WordLst[PosChar]
    # Appends new character to Plane Text
    PlainText += DecodedChar
    if Debug: print("[" + inChar + "] " + ShiftLst + " SFT["+ str(Shift).rjust(2, ' ') + "] POS["+ str(PosChar).rjust(2, ' ') + "] = [" + DecodedChar + "]")

    # Checks to see that we have not used all the Rotate Values, if so it starts over.
    if Rotator == len(Rotate) - 1:
        Rotator = 0
    else:
        Rotator += 1


print(" ")
print("Encrypted: " + inText)
print("Decrypted: " + PlainText)
print(" ")


