# Enigma
def sanitize(x):
    lettersonly = ""
    for i in range(len(x)):
        if x[i].isalpha():
            lettersonly += x[i]
    lettersonly = lettersonly.upper()
    #remove the spaces to confuse the enemy
    return lettersonly

#variables

reflector_settings = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
rotor1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
rotor2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
rotor3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#plugboard pairs
my_pairs = "bq cr di ej kw mt os px uz gh"

message = input("enter a string: ")
message = sanitize(message)

result = ""

#count variables
count1 = 1
count2 = 2
count3 = 3
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

def make_plugboard(pairs):
    splitpairs = pairs.split()
    print(splitpairs)
    plugboard = {}
    for i in range(len(splitpairs)):
        x = sanitize(splitpairs[i])
        plugboard[x[0]] = x[1]
        plugboard[x[1]] = x[0]
    return(plugboard)


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

def checkDiff(str1, str2):
    str1 = sanitize(str1)
    str2 = sanitize(str2)
    print(len(str1))
    print(len(str2))
    for i in range(len(str1)):
        if(str1[i] != str2[i]):
            print("The strings are different at positions (" + str(i) +") : \n str1 is at " + str(str1[i]) + "  str2 is at " + str(str2[i]))

#------------------------------------ reflector _____________________________________

def make_reflector(reflector_settings):
    reflector = {}
    for i in range(len(reflector_settings)):
        reflector[chr(65 + i)] = reflector_settings[i]
    return reflector


my_reflector = make_reflector(reflector_settings)
r1f = make_reflector(rotor1)
r2f = make_reflector(rotor2)
r3f = make_reflector(rotor3)
print(r1f.items() , "\n")
print(r2f.items() , "\n")
print(r3f.items() , "\n")
print(my_reflector)


r1b = {y:x for x,y in r1f.items()}
r2b = {y:x for x,y in r2f.items()}
r3b = {y:x for x,y in r3f.items()}
print(r1b.items() , "\n")
print(r2b.items() , "\n")
print(r3b.items() , "\n")

def letterShift(letter, count):
    x = ord(letter) + count
    if x < 65:
        x+=26
    if x > 90:
        x-=26
    return chr(x)

def rotorShift(letter, count, rotor):

    x = letterShift(letter, count)

    x = rotor[x]

    x = letterShift(x, -count)

    return x


for i in range(len(message)):
    if i%100000 == 0:
        print(i)
    count3 = ((count3 +1)%26)
    if count3 == ord(notch3) - 65:
        count2 = (count2 + 1) % 26
    if(count3 == ((ord(notch3) - 65) + 1) and count2 == ((ord(notch2) - 65) - 1)):
        count1 = (count1+1)%26
        count2 = (count2+1)%26



    cur_letter = message[i]
    output_letter = rotorShift(cur_letter, count3, r3f)

    output_letter = rotorShift(output_letter, count2, r2f)

    output_letter = rotorShift(output_letter, count1, r1f)

    #reflector
    output_letter = my_reflector[output_letter]

    output_letter = rotorShift(output_letter, count1, r1b)

    output_letter = rotorShift(output_letter, count2, r2b)

    output_letter = rotorShift(output_letter, count3, r3b)

    result+= output_letter


result = apply_plugboard(result, my_plugboard)

print(count3, count2, count1)
print(result)
