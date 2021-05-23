import os

from discord.ext import commands

bot = commands.Bot(command_prefix="yt ", help_command=None)

@bot.event
async def on_ready():
  print("Ready!")

for file in os.listdir("./src"):
  if file.endswith(".py"):
    bot.load_extension(f"src.{file[:-3]}")

bot.run(os.getenv("TOKEN"))