import random
from typing import List, Union
from DiscordUtils import Embed, ErrorEmbed
import aiohttp
import discord, asyncio
import orjson
from discord.ext import commands
from lib import (Characters, LinksAndVars, MemberID,
                 ShinobiMatchCharacterSelection, cache, MatchHandlerView)


class ShinobiMatchCog(commands.Cog, name='Shinobi Match'):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'An amazing shinobi match with your friends'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f5e1")
    
    @staticmethod
    @cache()
    async def characters_data(ctx:commands.Context) -> List[Characters]:
        async with aiohttp.ClientSession() as session:
            async with session.get(LinksAndVars.character_data.value) as resp:
                character_data: dict = orjson.loads(await resp.text())
        return [Characters.from_record(character_data[i], ctx, i) for i in character_data]
    
    @classmethod
    async def return_random_characters(self, ctx:commands.Context) -> List[Characters]:
        characters_data = await self.characters_data(ctx)
        random.shuffle(characters_data)
        return random.sample(characters_data, 25)
    
    @staticmethod
    def return_select_help_embed(author: discord.Member):
        embed= Embed(
            title='Select your character', 
            description='```\nSelect your character using which you will fight\n```\n Use to `dropdown` below to view the characters available and click the `confirm` button to confirm your character'
        )
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        return embed
    
    @commands.command(usage='<opponent.mention>')
    async def match(self, ctx:commands.Context, opponent: Union[discord.Member, MemberID]):
        '''Play shinobi match with your friends using the characters from `Naruto Verse`'''
        view1=ShinobiMatchCharacterSelection(characters_data=await self.return_random_characters(ctx), player=ctx.author, ctx=ctx)
        select_msg1: discord.Message = await ctx.send(embed=self.return_select_help_embed(ctx.author), view=view1) 

        view2=ShinobiMatchCharacterSelection(characters_data=await self.return_random_characters(ctx), player=opponent, ctx=ctx)
        select_msg2: discord.Message = await ctx.send(embed=self.return_select_help_embed(opponent), view=view2) 
        
        await view1.wait()
        await view2.wait()

        if view1.character is None or view2.character is None: 
            return await ctx.send(embed=ErrorEmbed(title="One of the shinobi didn't choose his character on time."))
        
        await select_msg1.delete()
        await select_msg2.delete()

        timer = await ctx.send('Starting the match in `3 seconds`')
        for i in range(1,3):
            await timer.edit(f'Starting the match in `{3-i} seconds`')
            await asyncio.sleep(1)
        await timer.delete()
        
        view = MatchHandlerView(player1 = (ctx.author, view1.character), player2 = (opponent, view2.character))
        view.message = await ctx.send(content=f'{ctx.author.mention} now your turn',embed=view.make_embed(), view=view)


def setup(bot):
    bot.add_cog(ShinobiMatchCog(bot))
