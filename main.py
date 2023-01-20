import discord
import Config
from discord.ext import commands
from youtube_dl import YoutubeDL
import random
import aiohttp

YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'False', 'simulate': 'True', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f'Бот {client.user}сейчас работает')


@client.command()
async def roll(ctx):
    await ctx.send(ctx.author.mention + f",ваше случайное число :{random.randint(1, 100)}")


@client.command()
async def play(ctx, url):
    vc = await ctx.message.author.voice.channel.connect()

    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in url:
            info = ydl.extract_info(url, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]

    link = info['formats'][0]['url']

    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS))
    await ctx.send('Сейчас воспроизводится: {}'.format(info['title']))


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.pause()
            await ctx.send("Музыка поставлена на паузу")
        else:
            await ctx.send("Музыка уже остановленна")
    except AttributeError:
        await ctx.send("Бот не в голосовом канале!")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_paused():
            voice.resume()
            await ctx.send('Проигрование музыки возобнавлено')
        else:
            await ctx.send("Музыка не на паузе")
    except AttributeError:
        await ctx.send("Бот не в голосовом канале!")


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        if voice.is_connected():
            await voice.disconnect()
            await ctx.send('Бот покинул голосовой канал')
    except AttributeError:
        await ctx.send("Бот не в голосовом канале!")


@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, limit: int):
    try:
        await ctx.channel.purge(limit=limit)
        await ctx.send('{} удалил сообщения'.format(ctx.author.mention))
        await ctx.send(f'количество удаленных сообщений: {limit}')
    except AttributeError:
        await ctx.send("У вас недостаточно прав")


@client.command()
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        request = await session.get('https://some-random-api.ml/img/dog')  # создание запроса
        dogjson = await request.json()  # преобразование в словарь
        embed = discord.Embed(title="Doggo!", color=discord.Color.random())  # создание эмбеда
        embed.set_image(url=dogjson['link'])
    await ctx.send(embed=embed)


@client.command()
async def commands(ctx):
    msg = '''
!play (название испольнитель/название песни/ссылка) - вы
!stop - Пауза музыки
!resume - Возобнавление музыки
!leave - бот покидает голосовой канал
!clear (количество сообщений) - удаление сообщений(необходимы права администратора)
!server - информация о сервере,количество участников 
!info - информация о пользователях сервера
!dog - случайные фото собак
!roll - случайное число от 1 до 100
    
    
    '''
    await ctx.send(msg)


@client.command()
async def server(ctx):
    await ctx.send(
        f"Название сервера:{ctx.guild.name} \nУчастников:{ctx.guild.member_count}")


@client.command()
async def info(ctx, user: discord.User = None):
    if user == None:
        user = ctx.message.author
    inline = True
    embed = discord.Embed(title=user.name + '#' + user.discriminator)
    userData = {
        "Упоминание": user.mention,
        "Никнейм": user.nick,
        "Учетная запись создана": user.created_at.strftime("%b %d %Y %T"),
        "Присоединился к серверу": user.joined_at.strftime("%b %d %Y %T"),
        "сервер": user.guild,
        "Топ роль": user.top_role
    }
    for [fieldName, fieldVal] in userData.items():
        embed.add_field(name=fieldName + ":", value=fieldVal, inline=inline)
    embed.set_footer(text=f"id: {user.id}")
    embed.set_thumbnail(user.display_avatar)
    await ctx.send(embed=embed)


client.run(Config.token)
