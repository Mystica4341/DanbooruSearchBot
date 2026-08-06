import discord
from discord.ext import commands, tasks
import faker

class IdleModule(commands.Cog):
    # Contructor 
    def __init__(self, bot):
      # Initialize Faker instances for Vietnamese and English locales
      self.bot = bot
      self.fake_VN = faker.Faker('vi_VN')
      self.fake_EN = faker.Faker('en_US')

      self.secret_word = ""
      self.is_active = False
      self.max_guesses = 6
      self.guesses_made = 0
      self.word_length = 5
      self.current_lang = 'vi'

    @commands.command(name='start_idle_game', description='Starts the idle game with a secret word in the specified language.')
    async def start_idle_game(self, interaction: discord.Interaction, lang: str = 'vi'):
        """Starts the idle game with a secret word in the specified language."""

        if self.is_active:
            await interaction.response.send_message("A game is already active. Please finish it before starting a new one.")
            return

        self.current_lang = lang.lower()
        if self.current_lang == 'vi':
            self.secret_word = self.fake_VN.word()
        elif self.current_lang == 'en':
            self.secret_word = self.fake_EN.word()
        else:
            await interaction.response.send_message("Invalid language. Please choose 'vi' for Vietnamese or 'en' for English.")
            return

        self.is_active = True
        self.guesses_made = 0
        await interaction.response.send_message(f"Idle game started! Guess the {self.word_length}-letter word in {self.current_lang.upper()}.")

    @commands.command(name='guess_word', description='Make a guess for the secret word.')
    async def guess_word(self, interaction: discord.Interaction, guess: str):
        """Make a guess for the secret word."""

        if not self.is_active:
            await interaction.response.send_message("No active game. Please start a new game using the 'start_idle_game' command.")
            return

        if len(guess) != self.word_length:
            await interaction.response.send_message(f"Your guess must be {self.word_length} letters long.")
            return

        self.guesses_made += 1

        if guess.lower() == self.secret_word.lower():
            await interaction.response.send_message(f"Congratulations! You've guessed the secret word '{self.secret_word}' in {self.guesses_made} guesses.")
            self.is_active = False
        else:
            if self.guesses_made >= self.max_guesses:
                await interaction.response.send_message(f"Game over! You've used all your guesses. The secret word was '{self.secret_word}'.")
                self.is_active = False
            else:
                await interaction.response.send_message(f"Incorrect guess. You have {self.max_guesses - self.guesses_made} guesses left.")