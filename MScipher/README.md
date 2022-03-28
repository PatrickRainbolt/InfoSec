# MScipher

MScipher (Multiple Shift Cipher) was a idea to create a multiple shift cipher, that uses a start shift value and a password. 
This may not improve the standard shift cipher but does make it more difficult to brute force.

#
# GNU Lesser General Public License v3.0
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.


# List of things to address:
```

+ Command line Parser and data checker
+ Command line Parser and data checker
----+ 

+ General Config in the code to make setup quicker:
 ---+ Boolean flags to add character sets to the established alphabet key
    ---+ Standard Set: ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
       ---+ If standard is set then all character are converted to Uppercase. 

       + Expanded Set: AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 0123456789
       +  Written Set: '.~,!@_?"\;:&`
       +     Math Set: +-*/<=>%$#^()|[]
 ---+ Command Line Arguments should be able to manipulate these flags.

+ Shift Direction:
 ---+ Set Direction Shift is performed.
    + Set Mid Direction Shift, based shift direction if value is above of below half 
        the value of the length of the established alphabet key. If the shift value is 
        less than or equal to it would shift Left, else if would shift right.
    + Custom Direction Shift, allows a pattern to be set for shifting. Example would 
        be, [Right, Right, Left, Right], then repeat. 

```
