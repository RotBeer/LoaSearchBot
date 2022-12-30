# This example requires the 'message_content' privileged intent to function.

from discord.ext import commands

import discord
import os
import loa

loa_search = loa.Loa_search()

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        ch_name = '악세자동검색'
        channel_id = [i.id for i in self.get_all_channels() if i.name == ch_name][0]
        channel = self.get_channel(channel_id)
        async for message in channel.history(limit=200):
            if message.author.id == self.user.id:
                await message.delete()
        
        await channel.send('악세자동검색 개발중!', view=StartButton())
        
class StartButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
        

    @discord.ui.button(label='생성하기', style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('원하는 옵션을 선택하고 생성을 눌러주세요', ephemeral=True, view=SelectOptions())
        self.value = True        

    @discord.ui.button(label='삭제하기', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('아직 안만들었어요', ephemeral=True, delete_after=3)
        
class DropdownCategory(discord.ui.Select):
    def __init__(self, parent):
        loa_EtcOptions = loa_search.action_options['EtcOptions']
        options = [
            discord.SelectOption(label='목걸이', value=200010),
            discord.SelectOption(label='귀걸이', value=200020),
            discord.SelectOption(label='반지', value=200030),
        ]
        super().__init__(placeholder='카테고리 선택', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        view: SelectOptions = self.view
        view.data_dict['category'] = self.values[0]
        await interaction.response.defer()

class DropdownItemgradequality(discord.ui.Select):
    def __init__(self, parent):
        self.parent = parent
        options = [discord.SelectOption(label=f'{item*10} 이상', value=item*10) for item in range(10)]

        super().__init__(placeholder='품질 선택', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.parent.data_dict['category'] = self.values[0]
        await interaction.response.defer()

class DropdownItemgrade(discord.ui.Select):
    def __init__(self, parent):
        self.parent = parent
        options = [
            discord.SelectOption(label=f'유물', value='유물'),
            discord.SelectOption(label=f'고대', value='고대'),
        ]

        super().__init__(placeholder='등급 선택', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.parent.data_dict['category'] = self.values[0]
        await interaction.response.defer()

class DropdownStat(discord.ui.Select):
    def __init__(self, parent, order):
        self.parent = parent
        self.order = order
        loa_EtcOptions = [item for item in loa_search.action_options['EtcOptions'] if item['Value'] == 2][0]
        options = [discord.SelectOption(label=item['Text'], value=item['Value']) for item in loa_EtcOptions['EtcSubs']]

        super().__init__(placeholder=f"{loa_EtcOptions['Text']} {self.order} 선택", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.parent.data_dict['category'] = self.values[0]
        await interaction.response.defer()

class DropdownAbillity(discord.ui.Select):
    def __init__(self, parent, order):
        self.parent = parent
        self.order = order
        loa_EtcOptions = [item for item in loa_search.action_options['EtcOptions'] if item['Value'] == 3][0]
        options = [discord.SelectOption(label=item['Text'], value=item['Value']) for item in loa_EtcOptions['EtcSubs']]

        super().__init__(placeholder=f"{loa_EtcOptions['Text']} {self.order} 선택", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.parent.data_dict['category'] = self.values[0]
        await interaction.response.defer()

class SelectOptions(discord.ui.View):
    def __init__(self):        
        super().__init__(timeout=None)
        self.data_dict = {}
        # self.add_item(DropdownCategory(self))
        # self.add_item(DropdownItemgradequality(self))
        # self.add_item(DropdownItemgrade(self))
        # self.add_item(DropdownStat(self, 1))
        

bot = Bot()
bot.run(os.environ['discord_token'])