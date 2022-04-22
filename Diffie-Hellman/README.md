# Diffie-Hellman algorithm

Diffie Hellman (DH) key exchange algorithm is a method for securely exchanging cryptographic keys over a public communications channel. Keys are not actually exchanged – they are jointly derived. It is named after their inventors Whitfield Diffie and Martin Hellman.

If Alice and Bob wish to communicate with each other, they first agree between them a large prime and a Primitive Root number. These numbers become a constant in the cipher and has to be share in both the crypter and decrypter function.



```
The Program Prime:---[ 91898348362451036710395092856725687899937294747427119332863802924486436207345 ]
The Primitive Root:--[ 725 ]

Alice Private Key:---[ 863 ]
Bob Private Key:-----[ 625 ]

Alice calculates her public key:  AlicePublicKey = root ^ AlicePrivateKey mod Prime :
-[ 64244479149137817105639209375494696808935276774910178722006187612267175211445 ]

Bob calculates his public key:    BobPublicKey = root ^ BobPrivateKey mod prime :
-[ 86329886034307255138656171064862683695876510772446891329087212668136834039820 ]


*** How to calculate the Password from their keys ***
Alice calculates the shared key as Key = BobPublicKey ^ AlicePrivateKey mod prime :
-[ 76358577946142858257437971863139926833739448910830194839798541491320222935435 ]

Bob calculates the shared key as Key = ALicePublicKey ^ BobPrivateKey mod prime :
-[ 76358577946142858257437971863139926833739448910830194839798541491320222935435 ]
```
