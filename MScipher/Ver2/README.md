# MSencode: 
MSencode is a Shift Cipher but every character has a unique shift table. This is accomplished by adding in a Rotation key or Password to the Cipher.

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


# Here is a example of the encryption process
```
]-[ ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789  --LEN[36]
]-[ FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE  --SHIFT[5]
 
]-[ Rotators[10, 31, 13, 13, 17, 9, 12, 34]
 
[T] PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO SFT[15] POS[19] = [8]
[h] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[10] POS[ 7] = [R]
[i] XYZ0123456789ABCDEFGHIJKLMNOPQRSTUVW SFT[23] POS[ 8] = [5]
[s] ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 SFT[36] POS[18] = [S]
[ ] RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQ SFT[17] POS[-1] = [Q]
[i] 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ SFT[26] POS[ 8] = [8]
[s] CDEFGHIJKLMNOPQRSTUVWXYZ0123456789AB SFT[ 2] POS[18] = [U]
[ ] ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 SFT[36] POS[-1] = [9]
[a] KLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJ SFT[10] POS[ 0] = [K]
[ ] FGHIJKLMNOPQRSTUVWXYZ0123456789ABCDE SFT[ 5] POS[-1] = [E]
[t] STUVWXYZ0123456789ABCDEFGHIJKLMNOPQR SFT[18] POS[19] = [B]
[e] 56789ABCDEFGHIJKLMNOPQRSTUVWXYZ01234 SFT[31] POS[ 4] = [9]
[s] MNOPQRSTUVWXYZ0123456789ABCDEFGHIJKL SFT[12] POS[18] = [4]
[t] VWXYZ0123456789ABCDEFGHIJKLMNOPQRSTU SFT[21] POS[19] = [E]
 
Decrypt: This is a test
Encrypt: 8R5SQ8U9KEB94E


```


