import os
import random

import interactions
from interactions import Embed, OptionType, SlashContext, slash_command, slash_option

bot = interactions.Client()
TOKEN = os.getenv('TOKEN')

keycaps = [
    "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
]


@interactions.listen()
async def on_startup():
  print("Bot is ready! Let's hunt some monsters!")


@slash_command(name="roll", description="Roll some d10s for the Hunter game.")
@slash_option(name="amount",
              description="The amount of dice to roll.",
              required=True,
              opt_type=OptionType.INTEGER)
@slash_option(name="difficulty",
              description="The difficulty level of the roll. (Default: 6)",
              required=False,
              opt_type=OptionType.INTEGER)
@slash_option(
    name="specialisation",
    description="Is your character specialised for this roll? (Default: False)",
    required=False,
    opt_type=OptionType.BOOLEAN)
@slash_option(
    name="negating_ones",
    description="Do botches negate successes on this roll? (Default: True)",
    required=False,
    opt_type=OptionType.BOOLEAN)
@slash_option(
    name="willpower",
    description=
    "Did you spend willpower for this roll? (One auto-success, default: False)",
    required=False,
    opt_type=OptionType.BOOLEAN)
async def _roll(
    ctx: SlashContext,
    amount: int,
    difficulty: int = 6,
    specialisation: bool = False,
    negating_ones: bool = True,
    willpower: bool = False,
):
  embed = Embed()

  if amount < 1 or amount > 100:
    embed.add_field("Wrong number of dice...",
                    "Please pick an amount between 1 and 100.",
                    inline=False)
    await ctx.respond(embed=embed)
    return

  if difficulty <= 1 or difficulty > 10:
    embed.add_field("Nonsensical difficulty...",
                    "Please pick a difficulty between 2 and 10.",
                    inline=False)
    await ctx.respond(embed=embed)
    return

  dice = []
  keyc = []

  for _ in range(amount):
    td = random.randint(1, 10)
    dice.append(td)
    keyc.append(keycaps[td])

  dice_str = " ".join(keyc)

  successes = 0
  botches = 0

  for d in dice:
    if d >= difficulty:
      if d == 10 and specialisation:
        successes += 2
      else:
        successes += 1
    elif d == 1:
      botches += 1

  embed = Embed()

  roll_str = f"{ctx.author.display_name} rolls {amount}d10 with difficulty {difficulty}."
  if specialisation:
    roll_str += "\n    Specialisation selected (10s count as two successes)."

  if willpower:
    roll_str += "\n    Willpower was spent (+1 success)."
    successes += 1

  if not negating_ones:
    roll_str += "\n    Botches do not negate successes."
    botches = 0

  total_successes = successes
  net_successes = max(0, successes - botches)

  embed.add_field("HunterBot dice roll", roll_str, inline=False)

  result_str = ""

  if successes == 0 and botches > 0:
    result_str = "Botch!"
  elif net_successes == 0:
    result_str = "Failure!"
  else:
    result_str = "Success!"

  result_str += f"\n{dice_str}\n({total_successes} - {botches} = {net_successes} net successes)"
  embed.add_field("Result", result_str, inline=False)
  await ctx.respond(embed=embed)


bot.start(TOKEN)
