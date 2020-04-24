import discord
from tinydb import TinyDB, Query
from discord.ext import commands

bot = commands.Bot(command_prefix = 'lmt/', case_insensetive = True)
ADMINS = ['ΤχεΑμμιΡ#6109',] # вставьте сюда ники, которые могут удалять лимиты
TOKEN = '' # вставьте сюда токен вашего бота
db = TinyDB('data.json')
cb = TinyDB('chan.json')
ROLE = Query()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='lmt/hlp'))

@bot.event
async def on_member_update(before, after):
    guild = after.guild
    for i in db.all():
        i = guild.get_role(i['id'])
        if (i in set(before.roles + after.roles)):
            if (len(i.members) > db.search(ROLE.id == i.id)[0]['lmt']):
                channel = bot.get_channel(cb.search(ROLE.gld == guild.id)[0]['chn'])
                embed = discord.Embed(
                    type = 'rich',
                    description = f'Было замечено превышение лимита роли.\nАйди: {str(i.id)}. Юзер: **{str(after)}**.',
                    colour = discord.Colour.from_rgb(255, 40, 30),
                )
                embed.add_field(name = 'У участника была удалена роль:', value = f'**{i.name}** (<@&{i.id}>)')
                await channel.send(embed = embed)
                await after.remove_roles(i, reason = 'Модерация лимита')

@bot.command(name = 'set')
async def lmtset(ctx, limitrole : discord.Role, limit : int):
    if (len(limitrole.members) > limit):
        await ctx.send(f'`Участники с данной ролью: {str(len(limitrole.members))}/{str(limit)}.`')
    else:
        roleid = limitrole.id
        if (db.search(ROLE.id == roleid) == []):
            db.insert({'id' : roleid, 'lmt' : limit})
            await ctx.send(f'`Роль с айди {str(roleid)} добавлена в список лимитированных.`')
        else:
            await ctx.send('`Данная роль уже является лимитированной. Используйте lmt/del для удаления.`')

@bot.command(name = 'del')
async def lmtdel(ctx, limitrole : discord.Role):
    if (str(ctx.message.author) in ADMINS):
        db.remove(ROLE.id == limitrole.id)
        await ctx.send('`Лимит был успешно удалён.`')
    else:
        await ctx.send('`Вы не имеете права на удаление лимита роли.`')

@bot.command(name = 'chn')
async def lmtchn(ctx):
    guild = ctx.guild
    channel = ctx.message.channel
    if (cb.search(ROLE.guild == guild) == []):
        cb.insert({'gld' : guild.id, 'chn' : channel.id})
    else:
        cb.remove(ROLE.gld == guild)
        cb.insert({'gld' : guild.id, 'chn' : channel.id})
    await ctx.send('`Канал оповещений выставлен.`', delete_after = 3.0)

@bot.command(name = 'hlp')
async def lmthlp(ctx):
    embed = discord.Embed(
        type = 'rich',
        description = 'Список команд ЛимитБота',
        colour = discord.Colour.from_rgb(255, 40, 30)
    )
    embed.add_field(name = 'Помощь', value = '`lmt/hlp` - команда для вызова этого сообщения.')
    embed.add_field(name = 'Канал оповещений', value = '`lmt/chn` для установки канала оповещений бота (логи).')
    embed.add_field(name = 'Лимит на роль', value = '`lmt/set @роль лимит` для устновки лимита для роли.\nНе работает, если участников с этой ролью больше лимита.')
    embed.add_field(name = 'Удаление лимита', value = '`lmt/del @роль` для удаления лимита роли. Использовать может только Гориго.')
    await ctx.send(embed = embed)

bot.run(TOKEN)
