# MScipher:  03-28-2022 
MScipher is a Shift Cipher but every character has a unique shift table. This is accomplished by adding in a Rotation key or Password to the Cipher. This is a proof of concept so encrypt and decrypt are two seperate scripts.

# So what is a shift cipher? 
It is a simple substitution cipher where the clear-text is shifted a number of times up or down a known alphabet. Here is an example where we have shifted to the left ‘5’ positions:
```
Plane:	    0123456789
Shifted:    5678901234
```

So where the Plane number ‘1234’ would become ‘6789’ from the shifted table. Then to decode the message you just use the Shifted position to get the Plane number. 

#
#GNU Lesser General Public License v3.0

Permissions of this copyleft license are conditioned on making available complete source code of licensed works and modifications under the same license or the GNU GPLv3. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. However, a larger work using the licensed work through interfaces provided by the licensed work may be distributed under different terms and without source code for the larger work.

#
# MSencode: 
```
Example: MSencode.py 5 'PASSWORD' 'This is a test'
```

# Here are the rules to MSencode:
    • Have a established alphabet key. Both the encode and decode process rely on a set key. An example is, “ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789”.
    • Have a established first left shift value. An example is ‘5’.
    • Have a established Rotation key or Password. One rule is that the key must be made up from the established alphabet key. An example is ‘PASSWORD’.

# How does it work:
    1. First we create the original left shifted alphabet key from the shift value you included. Using the example above we end up with this left shifted alphabet key, “FGHIJKLMNOPQRSTUVWXYZ 0123456789ABCDE”.
    2. Creates an array of positions, each character of the given Rotation key or Password, using the left shifted alphabet key. An example of this array would be, ‘10, 32, 13, 13, 17, 9, 12, 35’. So the ‘P’ from the example ‘PASSWORD’ is now in position ‘10’. I decided to create these using the left shifted alphabet key to make brute-forcing much harder. 
    3. Time to encode the message:
        ◦ Take the current shift value and add the first Rotation key together. If that value is larger the the length of the established alphabet key then subtract the length of the established alphabet key. Here is a example: Shift is at ‘5’, the first Rotation key is ‘10’, therefor ‘5 + 10’ equals ‘15’. ‘15’ is not larger than the length of the established alphabet key, which is ‘36’. Note: once you get to the last Rotation key just reset to position ‘1’ and keep rotating. 
        ◦ Take this new shift value and create a new left shifted alphabet key from the established alphabet key. Using the new shift value of ‘15’ we end up with a new key, ‘PQRSTUVWXYZ0123456789ABCDEFGHIJKLMNO’.
        ◦ Look up the position of first character of the text to encode in the established alphabet key. An example would be, ‘T’ is position ‘19’. Position ‘19’ is the new key is ‘7’.
        ◦ Continue this process through all of the characters in the text to encode.

If you are using the above examples with plane text of ‘This is a test’, it will encrypted to ‘7R4RF6SYI2860A’.


# Here is a example of the encryption process
```
]-[ ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789  --LEN[37]
]-[ FGHIJKLMNOPQRSTUVWXYZ 0123456789ABCDE  --SHIFT[5]
 
]-[ Rotators[10, 32, 13, 13, 17, 9, 12, 35]
 
[T] PQRSTUVWXYZ 0123456789ABCDEFGHIJKLMNO SFT[15] POS[19] = [7]
[h] KLMNOPQRSTUVWXYZ 0123456789ABCDEFGHIJ SFT[10] POS[ 7] = [R]
[i] XYZ 0123456789ABCDEFGHIJKLMNOPQRSTUVW SFT[23] POS[ 8] = [4]
[s] 9ABCDEFGHIJKLMNOPQRSTUVWXYZ 012345678 SFT[36] POS[18] = [R]
[ ] QRSTUVWXYZ 0123456789ABCDEFGHIJKLMNOP SFT[16] POS[26] = [F]
[i] Z 0123456789ABCDEFGHIJKLMNOPQRSTUVWXY SFT[25] POS[ 8] = [6]
[s] ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 SFT[37] POS[18] = [S]
[ ] 89ABCDEFGHIJKLMNOPQRSTUVWXYZ 01234567 SFT[35] POS[26] = [Y]
[a] IJKLMNOPQRSTUVWXYZ 0123456789ABCDEFGH SFT[ 8] POS[ 0] = [I]
[ ] DEFGHIJKLMNOPQRSTUVWXYZ 0123456789ABC SFT[ 3] POS[26] = [2]
[t] QRSTUVWXYZ 0123456789ABCDEFGHIJKLMNOP SFT[16] POS[19] = [8]
[e] 23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ 01 SFT[29] POS[ 4] = [6]
[s] JKLMNOPQRSTUVWXYZ 0123456789ABCDEFGHI SFT[ 9] POS[18] = [0]
[t] STUVWXYZ 0123456789ABCDEFGHIJKLMNOPQR SFT[18] POS[19] = [A]
 
Decrypt: This is a test
Encrypt: 7R4RF6SYI2860A

```


#
# MSdecode: 
```
Example: MSdecode.py 5 'PASSWORD' '7R4RF6SYI2860A'
```
# Here are the rules to MSdecode:
    • They are exactly the same as MSencode

# How does it work:
    1. It also works like MSencode except the character position and character lookup list are switched.

