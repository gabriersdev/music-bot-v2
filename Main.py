import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from dotenv import load_dotenv

# Carregar variáveis do .env localmente
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

queue = []
current_voice_client = None

# Caminho do ffmpeg
ffmpeg_path = r'libs\ffmpeg\bin\ffmpeg.exe'


def download_audio(url):
  ydl_opts = {
    'format': 'bestaudio/best',
    'ffmpeg_location': r'\libs\ffmpeg\bin',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': '320',
    }],
    'outtmpl': 'song.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True
  }

  print(ydl_opts)

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
  return "song.mp3"


@bot.event
async def on_ready():
  print(f'Bot conectado como {bot.user}')
  await bot.tree.sync()  # Sincroniza os comandos da árvore de comandos


@bot.tree.command(name="ajuda", description="Exibe os comandos disponíveis")
async def ajuda(interaction: discord.Interaction):
  embed = discord.Embed(title="Comandos do Bot", color=discord.Color.blue())
  embed.add_field(name="/ajuda", value="Suporte", inline=False)
  embed.add_field(name="/play <url>", value="Toque uma música do YouTube!", inline=False)
  embed.add_field(name="/fila", value="Veja a fila de músicas na Playlist", inline=False)
  embed.add_field(name="/pular", value="Pule para a próxima música da fila", inline=False)
  await interaction.response.send_message(embed=embed)


@bot.tree.command(name="play", description="Toque uma música do YouTube")
async def play(interaction: discord.Interaction, url: str):
  global current_voice_client

  if interaction.user.voice is None or interaction.user.voice.channel is None:
    await interaction.response.send_message("Você precisa estar em um canal de voz!")
    return

  elif url.find('https://') == -1 or url.find("youtu") == -1:
    await interaction.response.send_message("O parâmetro informado não é uma URL do Youtube!")
    return

  voice_channel = interaction.user.voice.channel
  if current_voice_client is None or not current_voice_client.is_connected():
    current_voice_client = await voice_channel.connect(reconnect=True, timeout=60)

  queue.append(url)
  await interaction.response.send_message(f"Adicionado à fila: {url}")

  # Inicia a música imediatamente se nada estiver tocando
  if not current_voice_client.is_playing():
    await play_next(interaction)


async def play_next(interaction: discord.Interaction):
  global current_voice_client
  if len(queue) == 0:
    await interaction.followup.send("A fila acabou!")  # Usando followup para enviar mensagem adicional
    await current_voice_client.disconnect()
    current_voice_client = None
    return

  url = queue.pop(0)
  file_path = download_audio(url)

  # Passa o caminho do ffmpeg na execução do FFmpegPCMAudio
  current_voice_client.play(discord.FFmpegPCMAudio(file_path, options="-b:a 192k -bufsize 64k", executable=ffmpeg_path),
                            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop))
  await interaction.followup.send(f"Tocando agora: {url}")


@bot.tree.command(name="fila", description="Exibe a fila de músicas")
async def fila(interaction: discord.Interaction):
  if len(queue) == 0:
    await interaction.response.send_message("A fila está vazia!")
  else:
    await interaction.response.send_message("Fila de músicas:\n" + "\n".join(queue))


@bot.tree.command(name="pular", description="Pule para a próxima música da fila")
async def pular(interaction: discord.Interaction):
  if current_voice_client and current_voice_client.is_playing():
    current_voice_client.stop()
    await interaction.response.send_message("Pulando para a próxima música!")
  else:
    await interaction.response.send_message("Nenhuma música está tocando no momento.")


bot.run(TOKEN)
