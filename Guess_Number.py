import random
from typing import Optional


class GuessNumberGame:
    def __init__(self, lower_bound: int = 10, upper_bound: int = 20, max_attempts: int = 5) -> None:
        """
        Initialize the game with the provided bounds and maximum attempts.
        A random target number is chosen between lower_bound and upper_bound.
        """
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.max_attempts = max_attempts
        self.target_number = random.randint(self.lower_bound, self.upper_bound)

    def print_welcome_message(self) -> None:
        """Prints the welcome message and game instructions."""
        print("\nWelcome to the Number Guessing Game!")
        print(f"Try to guess the lucky number between {self.lower_bound} and {self.upper_bound}.")
        print(f"You have {self.max_attempts} attempts. Good luck!\n")

    def get_user_guess(self, attempt: int) -> int:
        """
        Prompts the user for a guess, validates the input, and returns the valid guess.
        This method continues prompting until a valid guess is provided.
        """
        while True:
            try:
                user_input = input(f"Attempt {attempt}/{self.max_attempts} - Enter your guess: ")
                guess = int(user_input)

                if guess < 0:
                    print("Only positive numbers allowed! Try again.")
                    continue

                if not (self.lower_bound <= guess <= self.upper_bound):
                    print(f"Please enter a number between {self.lower_bound} and {self.upper_bound}.")
                    continue

                return guess
            except ValueError:
                print("Invalid input! Please enter a valid number.")

    def provide_hint(self, guess: int) -> None:
        """Provides a hint to the user whether to guess higher or lower."""
        hint = "higher" if guess < self.target_number else "lower"
        print("❌ Oops! That's not the correct number.")
        print(f"Hint: Try a {hint} number.")

    def play(self) -> None:
        """Main method to run the game."""
        self.print_welcome_message()
        for attempt in range(1, self.max_attempts + 1):
            guess = self.get_user_guess(attempt)
            if guess == self.target_number:
                print("\n🎉 Congratulations! You've guessed the right number!")
                break
            else:
                self.provide_hint(guess)
        else:
            print(f"\n😔 You've used all attempts! The lucky number was {self.target_number}.")

        print("\nThanks for playing! See you next time.")


def main() -> None:
    game = GuessNumberGame()
    game.play()


if __name__ == "__main__":
    main()
