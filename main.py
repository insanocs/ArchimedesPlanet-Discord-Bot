from discord import Client, File
from discord.ext import commands
from get_data import get_chunk, render_chunk, get_image_data, get_chunks, differ, get_image
from time import sleep
from datetime import timedelta
from io import BytesIO
import json
from template import add_template, find_template_data
from PIL import Image
from quantize import dither
import keep_alive

keep_alive.keep_alive()

client = commands.Bot(command_prefix='.')

with open('config.json') as json_file:
    data = json.load(json_file)
    bot_name = data["BOT-NAME"]
    token = data["TOKEN"]


@client.event
async def on_ready():
    print(f'{bot_name} is online with {client.latency * 1000:.2f}ms! \nBot made by nisano, with some help from portasynthica\'s code.')

@client.command()
async def chunk(ctx, x, y):
    chunk_y = ((65536 // 2) + int(y)) // 256
    chunk_x = ((65536 // 2) + int(x)) // 256
    img = render_chunk(x, y)
    async with ctx.typing():
        with BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(f'Recebido chunk de nº {chunk_x}, {chunk_y}',file=File(fp=image_binary, filename='chunk.png'))
            image_binary.close()
@chunk.error
async def chunk_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('```Uso correto: .chunk <x> <y>```')
@client.command(aliases=['ct'])
async def chunk_template(ctx, x, y):
    attachment = ctx.message.attachments[0]
    url = attachment.url
    message = await ctx.channel.send(f'Requisitando chunks...')
    async with ctx.typing():
        h, w, chx, chy = get_chunks(x, y, get_image_data(url)[0], get_image_data(url)[1])
        await message.edit(content=f'Terminado, convertidos {h * w:,} pixels, carregados {chx + chy} chunks')
        await ctx.channel.send(f'terminado',file=File('multiplos.png'))
@client.command(aliases=['d'])
async def diff(ctx, x, y):
    attachment = ctx.message.attachments[0]
    url = attachment.url
    message = await ctx.channel.send('Requisitando chunks...')
    async with ctx.typing():
        try:
            h, w, chx, chy = get_chunks(x, y, get_image_data(url)[0], get_image_data(url)[1])
        except:
            await ctx.channel.send('A conexão com o jogo não é estável. Algo de errado aconteceu.')
        img = get_image(url)
        await message.edit(content=f'Terminado, convertidos {h * w:,} pixels, carregados {chx + chy} chunks.')
    async with ctx.typing():
        erros, non_transp, ungrayed = differ(x, y, img)
        with BytesIO() as image_binary:
            ungrayed.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(content=f'{non_transp - erros:,}/{non_transp:,} | {(non_transp - erros) / non_transp * 100:.2f}% completo | {erros:,} erros', file=File(fp=image_binary, filename='diff.png'))

@client.command(aliases=['t'])
async def template(ctx, oper, name, *args):
    if oper == 'add' or oper == 'a':
        x = args[0]
        y = args[1]
        attachment = ctx.message.attachments[0]
        url = attachment.url
        img = get_image(url)
        response = add_template(name, x, y, img, ctx.author.id)
        if response == 'repeated':
            await ctx.channel.send('Nome já usado.')
        else:
            await ctx.channel.send('Template adicionada')
    if oper == 'rem' or oper == 'remove' or oper == 'i':
        pass
    if oper == 'info' or oper == 'i':
        x, y, id_, filepath = find_template_data(name)
    if oper == 'diff' or oper == 'd':
        x, y, id_, filepath = find_template_data(name)
        img = Image.open(f'templates_folder/{filepath}')
        message = await ctx.channel.send('Requisitando chunks...')
        async with ctx.typing():
            #try:
            h, w, chx, chy = get_chunks(x, y, img.size[0], img.size[1])
            await message.edit(content=f'Terminado, convertidos {h * w:,} pixels, carregados {chx + chy} chunks.')
            #except Exception as e:
                #await ctx.channel.send(f'A conexão com o jogo não é estável. Algo de errado aconteceu. {e}')
        async with ctx.typing():
            erros, non_transp, ungrayed = differ(x, y, img)
            with BytesIO() as image_binary:
                ungrayed.save(image_binary, 'PNG')
                image_binary.seek(0)
                await ctx.channel.send(content=f'{non_transp - erros:,}/{non_transp:,} | {(non_transp - erros) / non_transp * 100:.2f}% completo | {erros:,} erros', file=File(fp=image_binary, filename='diff.png'))
@client.command(aliases=['q'])
async def quantize(ctx, *args):
    if args[0] == 'default' or args[0] == '':
        attachment = ctx.message.attachments[0]
        url = attachment.url
        img = get_image(url)
        converted = dither(img)
        with BytesIO() as image_binary:
            converted.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.channel.send(content=f'Imagem convertida usando conversão default', file=File(fp=image_binary, filename='defaultConversion.png'))

client.run(f'{token}')