import datetime

import discord
from discord.ext import commands

class Misc(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief='Used to display the help menu', aliases=("h",), description="`yt help [command]`")
  async def help(self, ctx, command = None):
    if command:
      commands = [command.name.lower() for command in list(self.bot.commands)]

      if command.lower() not in commands:
        await ctx.send("That command does not exist. Maybe you used the alias of a command? Try the command again using the command name.")
        return

      command = list(self.bot.commands)[[command.name.lower() for command in self.bot.commands].index(command.lower())]

      desc = f"**Prefix** - `yt`\n\n**Syntax**:\n`[]` - Denotes optional arguments\n`<>` - Denotes required arguments\n`()` - Used to provide extra info on a certain argument\n\nCommand Name - `{command.name}`\nDescription - `{command.brief}`\nAliases - `{', '.join(command.aliases)}`\nCommand Format - {command.description}"

      embed = discord.Embed(
        title="Help Menu",
        description=desc,
        color=discord.Color.green()
      )

      embed.set_footer(text = f"Requested by {ctx.author.name}#{ctx.author.discriminator}", icon_url = ctx.author.avatar_url)

      await ctx.send(embed=embed)
      return

    desc = "**Prefixes** - `yt`\n\nUse `yt help [command]` for more help on a command\n\n"

    for cog in list(self.bot.cogs.keys()):
      desc += f"**{cog}**\n"

      lower_cogs = [key.lower() for key in self.bot.cogs.keys()]

      for command in self.bot.get_cog(list(self.bot.cogs.keys())[lower_cogs.index(cog.lower())]).walk_commands():
        desc += f"**`{command.name}`** - {command.brief}\n"

      desc += "\n"

    embed = discord.Embed(
      title='Help Menu',
      description=desc,
      color=discord.Color.green()
    )

    embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)

  @commands.command(aliases=("inv", "i"), brief="Used to invite my bot to your servers", description="`yt invite`")
  async def invite(self, ctx):
    embed = discord.Embed(
      title="Invite my bot here!",
      url="https://discord.com/api/oauth2/authorize?client_id=722011282068209736&permissions=8&scope=bot",
      color=discord.Color.green(),
      timestamp=datetime.datetime.now()
    )

    embed.set_footer(text=f"Requested by {await self.bot.fetch_user(ctx.author.id)}", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Misc(bot))