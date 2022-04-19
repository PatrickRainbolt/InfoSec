#!/usr/bin/python3
#--------------------------------------------------------------------------------------------------
# MScipher is a Shift Cipher but every character has a unique shift table. This is accomplished by
#    adding in a Rotation key or Password to the Cipher.
#
#                                                                      Writen by: Patrick Rainbolt
#--------------------------------------------------------------------------------------------------
import sys
import re

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
                              value on a valid charater in the List.
     {-p} or {--password}  Ask for the Rotate Key or Password after running.
     {-u} or {--upper}     Sets MScipher to Uppercase all Alphabetic Characters.

     {--minimal}    Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789} This is the Default.
     {--standard}   Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789}
     {--enlarged}   Sets Key to {ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz}
     {--expanded}   Sets Key to {AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 0123456789}

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
         elif ARG[1][0] != "-": inData = ARG[1]
         del ARG[1]
         DebugOut += "\n"

     if inData == "":
         # No Text was found in the Arguments, checking STDIN for Text,
         if not sys.stdin.isatty():
             inData = sys.stdin.read()[:-1]
         if inData == "": 
             SyntaxInformation()

     if Debug: print(DebugOut)
     if PassSet: Password = input('Please Enter a Password:')
     if Debug:
         print("- LEN[" + str(len(WordList)).rjust(2, ' ') + "] LST["+ WordList +"]")
         print("- LEN[" + str(len(Password)).rjust(2, ' ') + "] PAS["+ Password +"]")
     return inData

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
CmdText = CmdLineParser()
if Infile != "":
    print("ready!")

if CmdText == "":
    print("oppps!")

Shift = CreateShift(Shift, WordList, Debug)
Cipher = Ceasar(Shift, Justify, WordList, False)
LenCipher = len(Cipher)
Rotate = CreateRotators(Cipher, Password, Convert, Debug)

if DeCipher: outText = Decrypt(Shift, Justify, Rotate, WordList, CmdText, Convert, Leap, Debug)
else: outText = Encrypt(Shift, Justify, Rotate, WordList, CmdText, Convert, Leap, Debug)

sys.stdout.write(outText)
print("")
