# MScipher: 
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
```

# Other implimentations:
MScipher reads STDIN, if there is no input text on the command line and pipes out to STDOUT. These allow you to 
pipe in and out data. Here is an Example:
```
> cat file.txt | MScipher-V2.py --shift 5 --justify "Mid" > encode.txt
```


# Here is a example of the encryption process
```
> MScipher-V2.py --shift 5 --justify "Mid" --password "THIS IS A TEST" --debug

MScipher Debug-Mode Active:
# ARGS[ 8]  ARG['--shift', '5', '--justify', 'Mid', '--password', 'THIS IS A TEST', '--debug']

- ARGS[ 8]  ARG[--shift] + [5]
- ARGS[ 6]  ARG[--justify] + [Mid]
- ARGS[ 4]  ARG[--password]
- ARGS[ 3]  ARG[THIS IS A TEST]
- ARGS[ 2]  ARG[--debug]

Please Enter a Password:PASSWORD
- LEN[36] LST[ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]
- LEN[ 8] PAS[PASSWORD]
- LEN[..] SHF[5]


- LEN[36] LST[FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE]
# CHAR[P] POS[10]
# CHAR[A] POS[31]
# CHAR[S] POS[13]
# CHAR[S] POS[13]
# CHAR[W] POS[17]
# CHAR[O] POS[ 9]
# CHAR[R] POS[12]
# CHAR[D] POS[34]
- LEN[ 8] ROT[10, 31, 13, 13, 17, 9, 12, 34]

- L[T] pSHF[ 5] ROT[10] PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO SFT[15] POS[19] = [8]
- L[H] pSHF[15] ROT[31] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[10] POS[ 7] = [R]
- R[I] pSHF[10] ROT[13] NOPQRSTUVWXYZ0123456789ABCDEFGHIJKLM SFT[23] POS[ 8] = [V]
- R[S] pSHF[23] ROT[13] ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 SFT[36] POS[18] = [S]
- L[ ] pSHF[36] ROT[17] RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQ SFT[17] POS[-1] = [ ]
- R[I] pSHF[17] ROT[ 9] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[26] POS[ 8] = [S]
- L[S] pSHF[26] ROT[12] CDEFGHIJKLMNOPQRSTUVWXYZ0123456789AB SFT[ 2] POS[18] = [U]
- R[ ] pSHF[ 2] ROT[34] ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 SFT[36] POS[-1] = [ ]
- L[A] pSHF[36] ROT[10] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[10] POS[ 0] = [K]
- L[ ] pSHF[10] ROT[31] FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE SFT[ 5] POS[-1] = [ ]
- R[T] pSHF[ 5] ROT[13] STUVWXYZ0123456789ABCDEFGHIJKLMNOPQR SFT[18] POS[19] = [B]
- R[E] pSHF[18] ROT[13] FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE SFT[31] POS[ 4] = [J]
- L[S] pSHF[31] ROT[17] MNOPQRSTUVWXYZ0123456789ABCDEFGHIJKL SFT[12] POS[18] = [4]
- R[T] pSHF[12] ROT[ 9] PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO SFT[21] POS[19] = [8]
 
- PlainText: THIS IS A TEST
- Encrypted: 8RVS SU K BJ48


> MScipher-V2.py --shift 5 --justify "Mid" --password "8RVS SU K BJ48" --decipher 
Please Enter a Password:PASSWORD

THIS IS A TEST 
```


