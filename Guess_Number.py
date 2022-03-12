class GuessNumber:
    def __init__(self):
        pass
    import random
    def x(self):
        ctr = 0
        while ctr <= 5:
            i = int(input("Enter A Number"))
            if i < 0:
                print("Positive Numbers Only")
                continue
            j = self.random.randint(10, 20)
            diff = j - i
            if diff < 0 or diff > 0:
                print("Entered number close to lucky one \n Please try again...")
                print("The random generated is " + str(j))
                ctr = ctr + 1
            if diff == 0:
                print("Well Done You have guessed the number right")
                print("The random generated is " + str(j))
                break
            if ctr == 6:
                print("You couldn't guess the number \n Good Luck Next Time ")

        print("END")
n = GuessNumber()
n.x()
