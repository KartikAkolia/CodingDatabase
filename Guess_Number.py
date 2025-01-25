import random

class GuessNumberGame:
    def __init__(self):
        self.max_attempts = 5
        self.lower_bound = 10
        self.upper_bound = 20
        self.target_number = random.randint(self.lower_bound, self.upper_bound)

    def play(self):
        print("\nWelcome to the Number Guessing Game!")
        print(f"Try to guess the lucky number between {self.lower_bound} and {self.upper_bound}.")
        print(f"You have {self.max_attempts} attempts. Good luck!\n")

        for attempt in range(1, self.max_attempts + 1):
            try:
                guess = int(input(f"Attempt {attempt}/{self.max_attempts} - Enter your guess: "))
                
                if guess < 0:
                    print("Only positive numbers allowed! Try again.")
                    continue
                if guess < self.lower_bound or guess > self.upper_bound:
                    print(f"Please enter a number between {self.lower_bound} and {self.upper_bound}.")
                    continue
                
                if guess == self.target_number:
                    print("\n🎉 Congratulations! You've guessed the right number!")
                    break
                else:
                    print("❌ Oops! That's not the correct number.")
                    hint = "higher" if guess < self.target_number else "lower"
                    print(f"Hint: Try a {hint} number.")
            except ValueError:
                print("Invalid input! Please enter a valid number.")
        else:
            print(f"\n😔 You've used all attempts! The lucky number was {self.target_number}.")
        
        print("\nThanks for playing! See you next time.")

if __name__ == "__main__":
    game = GuessNumberGame()
    game.play()
