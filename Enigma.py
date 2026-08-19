# Enigma I cipher engine (command line script).
# Reads a plaintext message from stdin, runs it through a simulation of the
# historical Enigma I machine (plugboard, three rotors, reflector B), and
# prints the resulting ciphertext. The same code path also decrypts: feeding
# ciphertext back in with identical settings reproduces the plaintext, since
# the Enigma signal path is symmetric.
#
# This file is byte-for-byte identical to "Enigma Cipher/Enigma.py" in the
# nested project folder; the two are duplicate copies of the same script,
# not divergent versions. index.html is a separate, self-contained browser
# front end: its embedded JavaScript reimplements this same cipher logic
# (rotor wiring, notch stepping, reflector, plugboard) so the machine can run
# in a page, with no runtime dependency between it and this script.

# Strip everything but letters and uppercase the result.
# Called to normalize raw input before enciphering, and again inside
# make_plugboard() to normalize each configured letter pair.
def sanitize(x):
    lettersonly = ""
    for i in range(len(x)):
        if x[i].isalpha():
            lettersonly += x[i]
    lettersonly = lettersonly.upper()
    #remove the spaces to confuse the enemy
    return lettersonly

#variables

# Historical Enigma I wiring tables: each string is a fixed substitution of
# the alphabet representing how a rotor or the reflector is wired internally.
reflector_settings = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
rotor1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
rotor2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
rotor3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Plugboard (Steckerbrett) wiring for this session: space-separated letter
# pairs that get swapped both before and after the rotor/reflector stage.
#plugboard pairs
my_pairs = "bq cr di ej kw mt os px uz gh"

# Entry point: read the operator's message and normalize it for enciphering.
message = input("enter a string: ")
message = sanitize(message)

result = ""

# Rotor position counters (0-25, the current letter offset of each rotor).
# count3 is the fast rotor and steps every keypress, count1 is the slow
# rotor. These are mutated in the main encipher loop below to model
# physical rotor stepping.
#count variables
count1 = 1
count2 = 2
count3 = 3
# Notch letters: when the fast/middle rotor reaches these positions it
# triggers the next rotor over to step, mimicking the physical notch.
#notch variables
notch3 = "W"

notch2 = "F"

#result variables
'''
with open('expected.txt', 'r') as file:
    expected = file.read().replace('\n', '')
    expected = sanitize(expected)
with open('input.txt', 'r') as file:
    message = file.read().replace('\n', '')
    message = sanitize(message)
'''
#------------------------------------ plugboard _____________________________________

# Build a letter-to-letter lookup table from a space-separated pairs string,
# e.g. "bq cr" becomes {'B':'Q','Q':'B','C':'R','R':'C'}. Called once at
# startup to turn my_pairs into my_plugboard.
def make_plugboard(pairs):
    splitpairs = pairs.split()
    #print(splitpairs)
    plugboard = {}
    for i in range(len(splitpairs)):
        x = sanitize(splitpairs[i])
        plugboard[x[0]] = x[1]
        plugboard[x[1]] = x[0]
    return(plugboard)


# Swap each letter of a message through the plugboard mapping, leaving
# unmapped letters unchanged. Called once on the input message before the
# rotor stage, and once on the enciphered result after it, since the
# plugboard sits at both ends of the physical signal path.
def apply_plugboard(message, plugboard):
    newmessage = ""
    for i in range(len(message)):
        if message[i] in plugboard:
            newmessage += plugboard[message[i]]
        else:
            newmessage += message[i]
    return(newmessage)


my_plugboard = make_plugboard(my_pairs)

message = apply_plugboard(message, my_plugboard)

# Debug helper: prints the position where two equal length strings first
# diverge, letter by letter. Not called anywhere in the current flow; left
# over from comparing ciphered output against expected.txt while testing.
def checkDiff(str1, str2):
    str1 = sanitize(str1)
    str2 = sanitize(str2)
    print(len(str1))
    print(len(str2))
    for i in range(len(str1)):
        if(str1[i] != str2[i]):
            print("The strings are different at positions (" + str(i) +") : \n str1 is at " + str(str1[i]) + "  str2 is at " + str(str2[i]))

#------------------------------------ reflector _____________________________________

# Turn a wiring string (26 letters, one substitution per alphabet position)
# into a letter-to-letter forward map. Used to build the reflector's
# substitution and, reused below, each rotor's forward wiring too.
def make_reflector(reflector_settings):
    reflector = {}
    for i in range(len(reflector_settings)):
        reflector[chr(65 + i)] = reflector_settings[i]
    return reflector


# Forward wiring maps: the reflector's own substitution, plus each rotor's
# forward (right to left) substitution at its neutral, unshifted position.
my_reflector = make_reflector(reflector_settings)
r1f = make_reflector(rotor1)
r2f = make_reflector(rotor2)
r3f = make_reflector(rotor3)
"""
print(r1f.items() , "\n")
print(r2f.items() , "\n")
print(r3f.items() , "\n")
print(my_reflector)
"""

# Backward (left to right) wiring maps for each rotor, built by inverting
# the forward map. Used on the return trip through the rotors, after the
# signal bounces off the reflector.
r1b = {y:x for x,y in r1f.items()}
r2b = {y:x for x,y in r2f.items()}
r3b = {y:x for x,y in r3f.items()}
"""
print(r1b.items() , "\n")
print(r2b.items() , "\n")
print(r3b.items() , "\n")
"""

# Shift a letter's character code by count positions, wrapping within A-Z.
# Used by rotorShift to move a letter into and back out of a rotor's current
# rotational offset before and after applying its wiring.
def letterShift(letter, count):
    x = ord(letter) + count
    if x < 65:
        x+=26
    if x > 90:
        x-=26
    return chr(x)

# Pass one letter through a single rotor at its current rotational offset:
# shift into the rotor's frame, apply its wiring substitution, then shift
# back out. Called six times per letter in the main loop below, three times
# on the way in through the forward maps and three on the way back through
# the backward maps.
def rotorShift(letter, count, rotor):

    x = letterShift(letter, count)

    x = rotor[x]

    x = letterShift(x, -count)

    return x


# Main encipher loop: steps the rotors for this keypress, then sends the
# letter through rotor III, II, I, the reflector, and back through I, II,
# III, mirroring the physical Enigma signal path. Mutates count1/count2/
# count3 (rotor positions) and appends to `result`.
for i in range(len(message)):
    if i%100000 == 0:
        print(i)
    # Fast rotor (III) steps on every keypress.
    count3 = ((count3 +1)%26)
    # Middle rotor (II) steps when the fast rotor passes its notch.
    if count3 == ord(notch3) - 65:
        count2 = (count2 + 1) % 26
    # Double-stepping: when the fast rotor is one past its notch and the
    # middle rotor is one before its own notch, the slow rotor (I) and the
    # middle rotor both step together, matching the real machine's quirky
    # stepping behavior.
    if(count3 == ((ord(notch3) - 65) + 1) and count2 == ((ord(notch2) - 65) - 1)):
        count1 = (count1+1)%26
        count2 = (count2+1)%26



    cur_letter = message[i]
    # Forward pass through the rotors: III, then II, then I.
    output_letter = rotorShift(cur_letter, count3, r3f)

    output_letter = rotorShift(output_letter, count2, r2f)

    output_letter = rotorShift(output_letter, count1, r1f)

    #reflector
    output_letter = my_reflector[output_letter]

    # Return pass through the rotors: I, then II, then III, using the
    # backward wiring maps.
    output_letter = rotorShift(output_letter, count1, r1b)

    output_letter = rotorShift(output_letter, count2, r2b)

    output_letter = rotorShift(output_letter, count3, r3b)

    result+= output_letter


# Final plugboard pass on the way out, mirroring the pass applied to the
# input message before it entered the rotors.
result = apply_plugboard(result, my_plugboard)

#print(count3, count2, count1)
print("Ciphered text: " + result)

#KQRCZZIBRZRLEPZCDLLGDFVOQMVHZDDQNIENDOZOERQIS