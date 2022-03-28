# MScipher

MScipher (Multiple Shift Cipher) was a idea to create a multiple shift cipher, that uses a start shift value and a password. 
This may not improve the standard shift cipher but does make it more difficult to brute force.



# List of things to address:
```

+ Command line Parser and data checker
----+ 

+ General Config in the code to make setup quicker.
----+ Boolean flags to add character sets to the established alphabet key
    ---+ Standard Set: ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
       + Expanded Set: AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 0123456789
       +  Written Set: '.~,!@_?"\;:&`
       +     Math Set: +-*/<=>%$#^()|[]
----+ Command Line Arguments should be able to manipulate these flags.

```
