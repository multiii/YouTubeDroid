import datetime
from typing import Iterable

import discord
import sqlite3
from discord.ext import commands
from youtubesearchpython import VideosSearch

class YouTube(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.menus = {}

  def has_row(self, check: str, qmark: Iterable) -> bool:
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    cur.execute(check, qmark)

    rows = cur.fetchall()

    con.close()

    return len(rows) != 0

  @classmethod
  async def send_info(self, ctx, video, searches):
    embed = discord.Embed(
      title=video["title"],
      url=video["link"],
      description=f'**Channel:** [{video["channel"]["name"]}]({video["channel"]["link"]})\n\n**Views:** `{video["viewCount"]["text"]}`\n\n**Published:** `{video["publishedTime"]}`\n\n**Duration:** `{video["accessibility"]["duration"]}`\n\n**Description:** `{video["descriptionSnippet"][-1]["text"] if video["descriptionSnippet"] != None else "No Description"}`',
      color=discord.Color.green(),
      timestamp=datetime.datetime.now()
    )

    embed.set_thumbnail(url=video["channel"]["thumbnails"][-1]["url"])
    embed.set_image(url=video["thumbnails"][-1]["url"])

    msg = await ctx.send(embed=embed)

    self.menus.update({ctx.author.id: (searches, video, "info")})

    await msg.add_reaction("▶️")

    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: ctx.author == u and str(r.emoji) == "▶️" and r.message == msg)

    await ctx.send(f'Here is your requested video!\n\n{video["link"]}')

  @classmethod
  async def _search(self, ctx, *, keyword=None, page: int=1):
    if not keyword:
      return await ctx.send("Command Usage: `yt!search <keyword>`")

    searches = VideosSearch(keyword, limit=9 * page).result()["result"][9 * page - 9:9 * page]
    desc = "Click on the respective reaction to watch the video\n\n"

    index = 9 * page - 8

    for video in searches:
      desc += f"`{index}.` [{video['title']}]({video['link']}) `{video['duration']}`\nㅤby [{video['channel']['name']}]({video['channel']['link']}) • {video['viewCount']['short']}\n\n"

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

    self.menus.update({ctx.author.id: (keyword, page, "search")})

    reactions = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣")

    if len(searches) != 0:
      for i, reaction in enumerate(reactions):
        await msg.add_reaction(reaction)

        if i + 1 >= len(searches):
          break

    reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: ctx.author == u and str(r.emoji) in reactions and r.message == msg)

    await msg.delete()

    if self.has_row(check="SELECT * FROM info_mode WHERE id = ?", qmark=(ctx.author.id,)):
      return await self.send_info(ctx, searches[reactions.index(reaction.emoji)], searches=searches)

    await ctx.send(f'Here is your requested video!\n\n{searches[reactions.index(reaction.emoji)]["link"]}')

  @classmethod
  async def _previous(self, ctx):
    if ctx.author.id not in self.menus:
      return await ctx.send("Couldn't find a previous menu to paginate.")

    menu = self.menus[ctx.author.id]

    if menu[2] == "search":
      if menu[1] > 1:
        return await self.search(ctx, keyword=menu[0], page=menu[1] - 1)

      return await ctx.send("You've already reached the first page in the menu.")

    if menu[2] == "info":

      if menu[0].index(menu[1]) > 0:
        return await self.send_info(ctx, video=menu[0][menu[0].index(menu[1]) - 1], searches=menu[0])

      return await ctx.send("You've already reached the first video on this page.")

  @classmethod
  async def _next(self, ctx):
    if ctx.author.id not in self.menus:
      return await ctx.send("Couldn't find a previous menu to paginate.")

    menu = self.menus[ctx.author.id]

    if menu[2] == "search":
      return await self.search(ctx, keyword=menu[0], page=menu[1] + 1)

    if menu[2] == "info":
      try:
        return await self.send_info(ctx, video=menu[0][menu[0].index(menu[1]) + 1], searches=menu[0])
      
      except IndexError:
        return await ctx.send("You've already reached the last video on this page.")

  @commands.command(aliases=("inf",), brief="Used to toggle info mode on or off", description="`yt info`")
  async def info(self, ctx):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    cur.execute("SELECT * FROM info_mode WHERE id = ?", (ctx.author.id,))

    rows = cur.fetchall()

    if len(rows) == 0:
      cur.execute("""INSERT INTO info_mode (id, is_info) VALUES (?, ?)""", (ctx.author.id, 1))

      await ctx.send("Info mode was turned on <:online:846059164593029181>")

      con.commit()
      return con.close()

    cur.execute("""DELETE FROM info_mode WHERE id = ?""", (ctx.author.id,))

    await ctx.send("Info mode was turned off <:off:846059204921524304>")

    con.commit()
    con.close()

  @commands.command(aliases=("s",), brief="Used to search for content on YouTube", description="`yt search <keyword>`")
  async def search(self, ctx, *, keyword=None, page: int=1):
    await self._search(ctx, keyword=keyword, page=page)

  @commands.command(aliases=("p", "prev"), brief="Used to switch to the previous page of a menu", description="`yt previous`")
  async def previous(self, ctx):
    await self._previous(ctx)

  @commands.command(aliases=("n",), brief="Used to switch to the next page of a menu", description="`yt next`")
  async def next(self, ctx):
    await self._next(ctx)
  
def setup(bot):
  bot.add_cog(YouTube(bot))