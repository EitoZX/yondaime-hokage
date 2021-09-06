import ast
import os
import time
from os.path import join
from pathlib import Path

import discord
import DiscordUtils
import dotenv
import sentry_sdk
from discord.ext import commands
from dislash import *

from bot_files.lib import PostStats, PaginatedHelpCommand, format_dt

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True
intents.presences = False
intents.integrations = True
intents.members = True


dotenv_file = os.path.join(Path(__file__).resolve().parent.parent / ".env")


def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname, 'False').strip('\n')


TOKEN = token_get('TOKEN')
sentry_link = token_get('SENTRY')


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = [')', 'm!', 'minato', 'minato ']

    if not message.guild:
        return 'm!'

    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.AutoShardedBot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=PaginatedHelpCommand(),
    enable_debug_events=True,
    allowed_mentions=discord.AllowedMentions(
        users=True,
        roles=True,
        everyone=True
    ),
    case_insensitive=False,
    owner_id=571889108046184449
)
bot._cache = {}

bot.version = str(token_get('BOT_VER'))
bot.local = ast.literal_eval(token_get('LOCAL').capitalize())

bot.start_time = discord.utils.utcnow()
bot.github = token_get('GITHUB')
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(
    strict=True).parent / join('botmain', 'bot', 'discord_bot_images')


bot.minato_dir = Path(__file__).resolve(strict=True).parent / \
    join('bot_files','discord_bot_images')
bot.minato_gif = [f for f in os.listdir(join(bot.minato_dir, 'minato'))]
bot.uptime = format_dt(bot.start_time,'R')


@bot.event
async def on_ready():
    cog_dir = Path(__file__).resolve(strict=True).parent / \
        join('bot_files','cogs')
    for filename in os.listdir(cog_dir):
        if os.path.isdir(cog_dir / filename):
            for i in os.listdir(cog_dir / filename):
                if i.endswith('.py'):
                    bot.load_extension(f'bot_files.cogs.{filename.strip(" ")}.{i[:-3]}')
        else:
            if filename.endswith('.py'):
                bot.load_extension(f'bot_files.cogs.{filename[:-3]}')
    difference = int(round(time.time() - bot.start_time.timestamp()))
    stats = bot.get_channel(819128718152695878) if not bot.local else bot.get_channel(869238107118112810)
    e = discord.Embed(title=f"Bot Loaded!",
                      description=f"Bot ready by **{time.ctime()}**, loaded all cogs perfectly! Time to load is {difference} secs :)", color=discord.Colour.random())
    e.set_thumbnail(url=bot.user.avatar.url)

    guild = bot.get_guild(
        747480356625711204) if not bot.local else bot.get_channel(869238107118112810)
    try:
        bot._cache[guild.id] = {}
        for invite in await guild.invites():
            bot._cache[guild.id][invite.code] = invite
    except:
        pass
    print('Started The Bot')

    try:
        await stats.send(embed=e)
    except:
        pass
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name='over Naruto'
        )
    )
    
    await PostStats(bot).post_guild_stats_all()
    print('Status Posted')
    
    if not bot.local:
        await bot.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='over Naruto'
            )
        )
        await PostStats(bot).post_commands()
        print('Commands Status Posted')
        await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name='over Naruto'
        )
    )


sentry_sdk.init(
    sentry_link,
    traces_sample_rate=1.0
)
try:
    division_by_zero = 1 / 0
except:
    pass

if bot.local:
    from pypresence import Presence
    try:
        client_id = '779559821162315787'
        RPC = Presence(client_id)
        RPC.connect()
        RPC.update(
            state="火 Minato Namikaze 火",
            large_image="fzglchm",
            small_image="m57xri9",
            details="Konichiwa, myself Minato Namikaze, \n Konohagakure Yondaime Hokage, \n\n I try my best to do every work as a Hokage",
            large_text="Minato Namikaze | 波風ミナト",
            small_text="Minato Namikaze",
            buttons=[{"label": "Invite", "url": "https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&scope=bot%20applications.commands"},
                     {"label": "Website",
                         "url": 'https://minato-namikaze.readthedocs.io/en/latest/'}
                     ]
        )
    except:
        pass

if __name__ == '__main__':
    try:
        bot.run(TOKEN, reconnect=True)
    except discord.PrivilegedIntentsRequired:
        print(
            "[Login Failure] You need to enable the server members intent on the Discord Developers Portal."
        )
    except discord.errors.LoginFailure:
        print("[Login Failure] The token inserted in config.ini is invalid.")
