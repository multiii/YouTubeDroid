import datetime

import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch

class YouTube(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.menus = {}

  @commands.command(aliases=("s",), brief="Used to search for content on YouTube", description="`yt search <keyword>`")
  async def search(self, ctx, *, keyword=None, page: int=1):
    if not keyword:
      return await ctx.send("Command Usage: `yt!search <keyword>`")

    searches = VideosSearch(keyword, limit=9 * page).result()["result"][9 * page - 9:9 * page]
    desc = "Click on the respective reaction to watch the video\n\n"

    index = 9 * page - 8

    for video in searches:
      desc += f"`{index}.` [{video['title']}](https://www.youtube.com/watch?v={video['id']}) `{video['duration']}`\nㅤby [{video['channel']['name']}]({video['channel']['link']}) • {video['viewCount']['short']}\n\n"

      index += 1

    embed = discord.Embed(
      title=f"Search results for {keyword}",
      description=desc,
      url=f"https://www.youtube.com/results?search_query={'+'.join(keyword.split(' '))}",
      color=discord.Color.green(),
      timestamp=datetime.datetime.now()
    )

    embed.set_footer(text=f"Requested by {await self.bot.fetch_user(ctx.author.id)}", icon_url=ctx.author.avatar_url)

    msg = await ctx.send(embed=embed)

    self.menus.update({ctx.author.id: (keyword, page)})

    reactions = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣")

    if len(searches) != 0:
      for i, reaction in enumerate(reactions):
        await msg.add_reaction(reaction)

        if i + 1 >= len(searches):
          break

    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: ctx.author == u and str(r.emoji) in reactions and r.message == msg)

    await msg.delete()

    await ctx.send(f'Here is your requested video!\n\nhttps://www.youtube.com/watch?v={searches[reactions.index(reaction.emoji)]["id"]}')

  @commands.command(aliases=("n",), brief="Used to switch to the next page of a menu", description="`yt next`")
  async def next(self, ctx):
    if ctx.author.id not in self.menus:
      return await ctx.send("Couldn't find a previous menu to paginate.")

    try:
      await self.search(ctx, keyword=self.menus[ctx.author.id][0], page=self.menus[ctx.author.id][1] + 1)

    except IndexError:
      await ctx.send("You've already reached the last page in the menu.")


def setup(bot):
  bot.add_cog(YouTube(bot))