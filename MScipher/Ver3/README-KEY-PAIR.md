# MScipher Key Pair: 
A function that was missing in this Cipher was the ability to have a <b>Public</b> and <b>Private</b> key. So by exchanging public keys, the information can be Ciphered by only using your Private key and their Public key.

# What cipher method are we using? 
I went with a Diffie-Hellman approach to generating key pairs. This is done by create a <b>Program Prime</b> and a <b>Primitive Root</b> for the MScipher. These values can be regenerate and edited into the code, but anyone that trades Public Keys with you has to have the same values in there code. Unless you have a specific reason to create a new cipher set, I woulld leave these as the defaults.
```
The Program Prime---[98348149859422759653449222024902527358447401882717513832658752589732178323087]
The Primitive Root--[112610998970462321170418252784376929165518212068608580368800985994928452406337]
```

# How do I regenerate a new set of values? 
```
[/home/ceasar]: MScipher-V3.py --keyroot
 The Program Prime: 101306026189110404562794223543610887302783980074780257137217063750443517305487
The Primitive Root: 105212168530198836448204951699665177964500386522309245063885784986679433581131 

NOTE: Copy and Paste these values into the default variables. Warning changing these variable
  will require new public keys and will not decode privious messages that used the old Key pairs.
  Anyone you are communicating with will also have to change their values to match these new Key pairs.
```

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
```

# What is a public and Private key pair? 
Instead of trading a <i>private password</i> you can exchange Public keys instead, which anyone can view, but only your private key will decipher the information. 

First, you are asked for a new Key Ring Password. That password is encoded with MScipher to get Rotator Position, then the Values are joined together
giving a <b>Password Value</b>. 

Second, a random <b>Private Key</b> is generated. This value is added to the <b>Password Value</b> and stored in a file called "MSc.prv". The Password is added before storing the key to make brute force attacks much more difficult. 

Third, a <b>Public key</b> is created by taking the <b>Primitive Root</b> Raised to the power of your <b>Private Key</b> and modular by <b>Program Prime</b>. This will generate a value that anyone can use to cipher messages with you.
```
[/home/ceasar]: MScipher-V3.py --keygen
Are you sure you want to generate Rotator Key Pairs, This will overwrite any other Keys (Yes or No): Yes
Please Enter a Key Password: mypassword

Generating Rotator Key Pairs:
- Public and Private Keys have been generated.
- Rotator Key Pairs have been generated and stored.

To view your Public Key: MScipher --keypublic

[/home/ceasar]: MScipher-V3.py --keypublic
MSpub:27795932278286082649526146816580757607424177962524698122986674033881123651396

```
The "27795932278286082649526146816580757607424177962524698122986674033881123651396" value after "MSpub:" is the Public key.

# How to add or delete someone to the Key Ring?
MScipher has two commands "--keyadd" and "--keydel" that accomplishes this task.  

```
[/home/ceasar]: MScipher-V3.py --keyadd "bob"
Enter Public Key for bob: 38942130306459146109341625640864409318756929387036866278864827954285392085988

MScipher: bob was added to the Rotator Key Ring.
```

# How to view your Key Ring?
MScipher command to view your public Key Ring is "--keylist".
```
[/home/ceasar]: MScipher-V3.py --keylist
MScipher Public Key Ring Storage File.
----------------------------------------------------------------------------------------------
bob:38942130306459146109341625640864409318756929387036866278864827954285392085988

```


# How to encrypt a message
When using Key Pairs the Password it request is your Key Ring Password.

```
[/home/ceasar]: MScipher-V3.py -s 5 -k "bob" "THIS IS A TEST" --debug

MScipher Debug-Mode Active:
# ARGS[ 7]  ARG['-s', '5', '-k', 'bob', 'THIS IS A TEST', '--debug']

- ARGS[ 7]  ARG[-s] + [5]
- ARGS[ 5]  ARG[-k] + [bob]
- ARGS[ 3]  ARG[THIS IS A TEST]
- ARGS[ 2]  ARG[--debug]

- LEN[36] LST[ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]
- LEN[..] SHF[5]

- Loading Public Key for bob [38942130306459146109341625640864409318756929387036866278864827954285392085988]
- Loading Your Private Key.
Please Enter your Key Ring Password: password

- Deciphering Private Key.
- LEN[39] ROT[12, 8, 9, 14, 14, 11, 36, 22, 13, 13, 14, 33, 14, 12, 34, 30, 16, 9, 35, 1, 5, 12, 11, 6, 9, 5, 1, 21, 9, 0, 6, 18, 11, 14, 6, 21, 20, 10, 9]

- L[T] pSHF[ 5] ROT[12] RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQ SFT[17] POS[19] = [A]
- L[H] pSHF[17] ROT[ 8] Z0123456789ABCDEFGHIJKLMNOPQRSTUVWXY SFT[25] POS[ 7] = [6]
- L[I] pSHF[25] ROT[ 9] 89ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567 SFT[34] POS[ 8] = [G]
- L[S] pSHF[34] ROT[14] MNOPQRSTUVWXYZ0123456789ABCDEFGHIJKL SFT[12] POS[18] = [4]
- L[ ] pSHF[12] ROT[14] 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ SFT[26] POS[-1] = [ ]
- L[I] pSHF[26] ROT[11] BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789A SFT[ 1] POS[ 8] = [J]
- L[S] pSHF[ 1] ROT[36] BCDEFGHIJKLMNOPQRSTUVWXYZ0123456789A SFT[ 1] POS[18] = [T]
- L[ ] pSHF[ 1] ROT[22] XYZ0123456789ABCDEFGHIJKLMNOPQRSTUVW SFT[23] POS[-1] = [ ]
- L[A] pSHF[23] ROT[13] ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 SFT[36] POS[ 0] = [A]
- L[ ] pSHF[36] ROT[13] NOPQRSTUVWXYZ0123456789ABCDEFGHIJKLM SFT[13] POS[-1] = [ ]
- L[T] pSHF[13] ROT[14] 123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0 SFT[27] POS[19] = [K]
- L[E] pSHF[27] ROT[33] YZ0123456789ABCDEFGHIJKLMNOPQRSTUVWX SFT[24] POS[ 4] = [2]
- L[S] pSHF[24] ROT[14] CDEFGHIJKLMNOPQRSTUVWXYZ0123456789AB SFT[ 2] POS[18] = [U]
- L[T] pSHF[ 2] ROT[12] OPQRSTUVWXYZ0123456789ABCDEFGHIJKLMN SFT[14] POS[19] = [7]
 
- PlainText: THIS IS A TEST
- Encrypted: A6G4 JT A K2U7
```


