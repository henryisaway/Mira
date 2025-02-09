import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

from colorama import init as coloramaINIT
from colorama import Fore
from colorama import Style
coloramaINIT()

# Modified configuration for SoundCloud without client ID
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractor_args': {
        'soundcloud': {
            'client_id': 'a3e059563d7fd3372b49b37f00a00bcf'
        }
    },
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
    }],
}

ffmpeg_options = {
    'options': '-vn -b:a 128k -bufsize 512k',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -nostdin'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                data = data['entries'][0]
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        except Exception as e:
            print(f"{Fore.RED}Extraction error: {e}{Style.RESET_ALL}")
            raise

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.repeat = False
        self.repeat_queue = False
        self.current_song = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Music cog listener is {Fore.GREEN}ready{Style.RESET_ALL}.")

    async def play_next(self, ctx):
        try:
            if self.repeat and self.current_song:
                return await self.play_song(ctx, self.current_song)
            
            if self.queue:
                self.current_song = self.queue.pop(0)
                await self.play_song(ctx, self.current_song)
                if self.repeat_queue and not self.repeat:
                    self.queue.append(self.current_song)
            else:
                self.current_song = None
                await ctx.voice_client.disconnect()
        except Exception as e:
            print(f"{Fore.RED}Playback error: {e}{Style.RESET_ALL}")
            await ctx.send("❌ Playback error occurred")

    async def play_song(self, ctx, song):
        try:
            source = await YTDLSource.from_url(song['url'], loop=self.bot.loop, stream=True)
            ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.handle_playback_end(ctx, e)))
            await ctx.send(f"**Now playing:** {source.title}")
        except Exception as e:
            await ctx.send(f"❌ Error playing song: {str(e)}")
            await self.play_next(ctx)

    async def handle_playback_end(self, ctx, error):
        if error:
            print(f"{Fore.RED}Playback error: {error}{Style.RESET_ALL}")
        await self.play_next(ctx)

    @commands.command(name='play', help='Play a song from SoundCloud')
    async def play(self, ctx, *, query):
        try:
            if not ctx.author.voice:
                await ctx.send("You're not in a voice channel!")
                return

            voice_channel = ctx.author.voice.channel
            
            if ctx.voice_client:
                if ctx.voice_client.channel != voice_channel:
                    await ctx.voice_client.move_to(voice_channel)
            else:
                await voice_channel.connect()

            # Add soundcloud search prefix if not URL
            if not query.startswith(('http://', 'https://', 'scsearch:')):
                query = f"scsearch:{query}"

            async with ctx.typing():
                data = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                song = {'url': query, 'title': data.title}
                
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    self.queue.append(song)
                    await ctx.send(f"**Added to queue:** {data.title}")
                else:
                    self.current_song = song
                    await self.play_song(ctx, song)
                    
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
            print(f"{Fore.RED}Play command error: {e}{Style.RESET_ALL}")

async def setup(bot):
    await bot.add_cog(Music(bot))
    print("Music module has finished loading.\n")