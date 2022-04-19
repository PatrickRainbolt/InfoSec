# MSencode: 
MScipher is a Shift Cipher but every character has a unique shift table. This is accomplished by adding in a Rotation key or Password to the Cipher.

# So what is a shift cipher? 
It is a simple substitution cipher where the clear-text is shifted a number of times up or down a known alphabet. Here is an example where we have shifted to the right ‘5’ positions:
```
Plane:	    0123456789
Shifted:    5678901234
```

So where the Plane number ‘1234’ would become ‘6789’ from the shifted table. Then to decode the message you just use the Shifted position to get the Plane number. 

# Here are the rules to Msencode:
    • Have a established alphabet key. Both the encode and decode process rely on a set key. An example is, “ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789”.
    • Have a established first right shift value. An example is ‘5’.
    • Have a established Rotation key or Password. One rule is that the key must be made up from the established alphabet key. An example is ‘PASSWORD’.

# How does it work:
    1. First we create the original right shifted alphabet key from the shift value you included. Using the example above we end up with this right shifted alphabet key, “FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE”.
    2. Creates an array of positions, each character of the given Rotation key or Password, using the right shifted alphabet key. An example of this array would be, ‘10, 31, 13, 13, 17, 9, 12, 34’. So the ‘P’ from the example ‘PASSWORD’ is now in position ‘10’. I decided to create these using the right shifted alphabet key to make brute-forcing much harder. 
    3. Time to encode the message:
        ◦ Take the current shift value and add the first Rotation key together. If that value is larger the the length of the established alphabet key then subtract the length of the established alphabet key. Here is a example: Shift is at ‘5’, the first Rotation key is ‘10’, therefor ‘5 + 10’ equals ‘15’. ‘15’ is not larger than the length of the established alphabet key, which is ‘36’. Note: once you get to the last Rotation key just reset to position ‘1’ and keep rotating. 
        ◦ Take this new shift value and create a new right shifted alphabet key from the established alphabet key. Using the new shift value of ‘15’ we end up with a new key, ‘PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO’.
        ◦ Look up the position of first character of the text to encode in the established alphabet key. An example would be, ‘T’ is position ‘19’. Position ‘19’ is the new key is ‘8’.
        ◦ Continue this process through all of the characters in the text to encode.

If you are using the above examples with plane text of ‘This is a test’, it will encrypted to ‘8R5SQ8U9KEB94E’.

# Program Syntax:
```
SYNTAX: MScipher <args> <passcode> <text>

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
```

# Here is a example of the encryption process
```
> MScipher-V2.py -s 5 -j "Mid" "PASSWORD" "THIS IS A TEST" --debug

MScipher Debug-Mode Active:
# ARGS[ 8]  ARG['-s', '5', '-j', 'Mid', 'PASSWORD', 'THIS IS A TEST', '--debug']

- ARGS[ 8]  ARG[-s] + [5]
- ARGS[ 6]  ARG[-j] + [Mid]
- ARGS[ 4]  ARG[PASSWORD]
- ARGS[ 3]  ARG[THIS IS A TEST]
- ARGS[ 2]  ARG[--debug]

- LEN[36] LST[ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]
- LEN[ 6] PAS[SECRET]
- LEN[..] SHF[5]


- LEN[36] LST[FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE]
# CHAR[S] POS[13]
# CHAR[E] POS[35]
# CHAR[C] POS[33]
# CHAR[R] POS[12]
# CHAR[E] POS[35]
# CHAR[T] POS[14]
- LEN[ 6] ROT[13, 35, 33, 12, 35, 14]

- R[T] pSHF[ 5] ROT[13] STUVWXYZ0123456789ABCDEFGHIJKLMNOPQR SFT[18] POS[19] = [B]
- L[H] pSHF[18] ROT[35] RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQ SFT[17] POS[ 7] = [Y]
- L[I] pSHF[17] ROT[33] OPQRSTUVWXYZ0123456789ABCDEFGHIJKLMN SFT[14] POS[ 8] = [W]
- R[S] pSHF[14] ROT[12] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[26] POS[18] = [2]
- R[ ] pSHF[26] ROT[35] LMNOPQRSTUVWXYZ0123456789ABCDEFGHIJK SFT[25] POS[-1] = [ ]
- L[I] pSHF[25] ROT[14] DEFGHIJKLMNOPQRSTUVWXYZ0123456789ABC SFT[ 3] POS[ 8] = [L]
- L[S] pSHF[ 3] ROT[13] QRSTUVWXYZ0123456789ABCDEFGHIJKLMNOP SFT[16] POS[18] = [8]
- L[ ] pSHF[16] ROT[35] PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO SFT[15] POS[-1] = [ ]
- L[A] pSHF[15] ROT[33] MNOPQRSTUVWXYZ0123456789ABCDEFGHIJKL SFT[12] POS[ 0] = [M]
- R[ ] pSHF[12] ROT[12] MNOPQRSTUVWXYZ0123456789ABCDEFGHIJKL SFT[24] POS[-1] = [ ]
- R[T] pSHF[24] ROT[35] NOPQRSTUVWXYZ0123456789ABCDEFGHIJKLM SFT[23] POS[19] = [6]
- L[E] pSHF[23] ROT[14] BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789A SFT[ 1] POS[ 4] = [F]
- L[S] pSHF[ 1] ROT[13] OPQRSTUVWXYZ0123456789ABCDEFGHIJKLMN SFT[14] POS[18] = [6]
- L[T] pSHF[14] ROT[35] NOPQRSTUVWXYZ0123456789ABCDEFGHIJKLM SFT[13] POS[19] = [6]
 
- PlainText: THIS IS A TEST
- Encrypted: BYW2 L8 M 6F66

```


