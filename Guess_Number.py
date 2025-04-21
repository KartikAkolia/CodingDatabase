import argparse
import logging
import random
import sys
from typing import Optional, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A robust number-guessing game with customizable bounds and attempts."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--difficulty', '-d',
        choices=['easy', 'medium', 'hard'],
        help="Predefined difficulty level (overrides other bounds/options)."
    )
    parser.add_argument(
        '--lower', '-l',
        type=int,
        default=1,
        help="Lower bound for the guessing range (inclusive)."
    )
    parser.add_argument(
        '--upper', '-u',
        type=int,
        default=100,
        help="Upper bound for the guessing range (inclusive)."
    )
    parser.add_argument(
        '--attempts', '-a',
        type=int,
        default=10,
        help="Maximum number of attempts allowed."
    )
    parser.add_argument(
        '--seed', '-s',
        type=int,
        help="Optional random seed for reproducibility (useful for testing)."
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose debug logging."
    )
    return parser.parse_args()


class GuessNumberGame:
    def __init__(
        self,
        lower_bound: int = 1,
        upper_bound: int = 100,
        max_attempts: int = 10,
        rng: Optional[random.Random] = None,
    ) -> None:
        # Validate parameters
        if lower_bound >= upper_bound:
            raise ValueError("Lower bound must be strictly less than upper bound.")
        if max_attempts <= 0:
            raise ValueError("Max attempts must be a positive integer.")

        self.lower_bound: int = lower_bound
        self.upper_bound: int = upper_bound
        self.max_attempts: int = max_attempts
        self.rng: random.Random = rng or random.Random()
        self.target_number: int = self.rng.randint(self.lower_bound, self.upper_bound)
        self.attempts: List[int] = []

        logging.debug(
            "Game initialized with range [%d, %d], attempts=%d", 
            self.lower_bound, self.upper_bound, self.max_attempts
        )

    def print_welcome(self) -> None:
        print("\n🎲 Welcome to the Number Guessing Game! 🎲")
        print(f"Guess a number between {self.lower_bound} and {self.upper_bound}.")
        print(f"You have {self.max_attempts} attempts. Good luck!\n")

    def get_guess(self, attempt: int) -> int:
        while True:
            try:
                guess_input = input(f"Attempt {attempt}/{self.max_attempts}. Your guess: ")
                guess = int(guess_input)
            except ValueError:
                print("❗ Please enter a valid integer.")
                continue
            except (KeyboardInterrupt, EOFError):
                print("\nExiting game. Goodbye!")
                sys.exit(0)

            if guess < self.lower_bound or guess > self.upper_bound:
                print(f"❗ Guess must be between {self.lower_bound} and {self.upper_bound}.")
                continue

            logging.debug("User guessed: %d", guess)
            return guess

    def provide_hint(self, guess: int) -> None:
        if guess < self.target_number:
            direction = "higher"
        else:
            direction = "lower"
        print(f"❌ Wrong. Try a {direction} number.")

    def play(self) -> None:
        self.print_welcome()
        for attempt in range(1, self.max_attempts + 1):
            guess = self.get_guess(attempt)
            self.attempts.append(guess)

            if guess == self.target_number:
                print(f"\n🎉 Congrats! You guessed it in {attempt} attempts.")
                break

            self.provide_hint(guess)
        else:
            print(f"\n☹️ Out of attempts! The correct number was {self.target_number}.")

        print("\nYour guesses: ", ", ".join(map(str, self.attempts)))

    def reset(self) -> None:
        """Reset the game for another round without recreating the object."""
        self.target_number = self.rng.randint(self.lower_bound, self.upper_bound)
        self.attempts.clear()
        logging.debug("Game reset for new round with new target %d", self.target_number)


def main() -> None:
    args = parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Predefined difficulties override bounds/attempts
    difficulty_settings = {
        'easy':   {'lower': 1,   'upper': 50,  'attempts': 15},
        'medium': {'lower': 1,   'upper': 100, 'attempts': 10},
        'hard':   {'lower': 1,   'upper': 200, 'attempts': 5},
    }
    if args.difficulty:
        params = difficulty_settings[args.difficulty]
        lower, upper, max_att = params['lower'], params['upper'], params['attempts']
    else:
        lower, upper, max_att = args.lower, args.upper, args.attempts

    rng = random.Random(args.seed) if args.seed is not None else None
    try:
        game = GuessNumberGame(lower, upper, max_att, rng)
    except ValueError as e:
        logging.error(str(e))
        sys.exit(1)

    while True:
        game.play()
        try:
            again = input("\nWould you like to play again? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Thanks for playing!")
            break

        if again in ('y', 'yes'):
            game.reset()
            print()
            continue
        print("Goodbye!")
        break


if __name__ == '__main__':
    main()
