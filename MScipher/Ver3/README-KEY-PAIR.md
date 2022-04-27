# MScipher Key Pair: 
A function that was missing in this Cipher was the ability to have a Public and Private key. So by exchanging public keys, the information can be Ciphered by only using your Private key and their Public key.

# So what is the cipher? 
I went with a Diffie-Hellman approach to generating key pairs. This is done by create a Program Prime and a Primitive Root for the MScipher. These values can be regenerate and edited into the code, but anyone that trades Public Keys with you has to have the same values in there code. Unless you have a specific reason to create a new cipher set, I woulld leave these as the defaults.
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

# What is a public and Private key pair? 
Instead of trading a Private Password, you can exchange a Public key instead, which anyone can view, but only your private key will decipher the information. 

First, you are asked for a Key Ring Password. That password is encoded with MScipher to get Rotator Position, then the Values are joined together
giving a Password Value. 

Second, a random Private Key is generated. This value is added to the Password Value and stored in a file called "MSc.prv". The Password is added before storing to make brute force attacks much more difficult. 

Third, a Public key is created by taking the Primitive Root Raised to the power of your Private Key and modular by Program Prime. This will generate a value that anyone can use to cipher messages with you.
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



