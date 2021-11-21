import random

i = int(input("Enter A Number"))
j = random.randint(10, 100)

while True:
    diff = j - i
    if diff < 0:
        print("You are well above the expected number")
        print("The random generated is " + str(j))
        exit()
    if diff == 0:
        print("Well Done You have guessed the number right")
        print("The random generated is " + str(j))
        exit()
    if 0 < diff < 10:
        print("You have almost guessed right number")
        print("The random generated is " + str(j))
        exit()