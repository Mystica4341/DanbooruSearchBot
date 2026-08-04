import discord
from discord.ext import commands, tasks
import faker

class IdleModule:
    # Contructor 
    def __init__(self, language='vi_VN', target_channel_id=None):
      # Initialize Faker instances for Vietnamese and English locales
      self.fake_VN = faker.Faker('vi_VN')
      self.fake_EN = faker.Faker('en_US')

      self.secret_word = ""
      self.is_active = False
      self.max_guesses = 6
      self.guesses_made = 0
      self.word_length = 5
      self.current_lang = 'vi'

    