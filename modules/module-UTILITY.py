import discord
from discord.ext import commands
import modules.utils as utils

from colorama import init as coloramaINIT
from colorama import Fore
from colorama import Style
coloramaINIT()
#-----------------------------------------------------------

class Utility(commands.Cog):

    # Constructor
    def __init__(self, bot):
        self.bot = bot
                
    @commands.Cog.listener()
    async def on_ready(self):

        print(f"Utility cog listener is {Fore.GREEN}ready{Style.RESET_ALL}.")
    
    #-------------------------------------------------------

    # Ping command: test command, used to check latency in milisseconds.
    @commands.command()
    async def ping(self, ctx):
        try:
            await ctx.reply(f"Pong! :ping_pong:\n**Latência**: {self.bot.latency * 1000:.0f}ms")
        except Exception as e:
            await ctx.reply(f"Um erro ocorreu: {e}")
    
    # Prefix command: Gets or sets the prefix of the current server
    @commands.command(aliases = ['prefixo'])
    async def prefix(self, ctx, new: str = None):
        try:
            if new is None:
                await ctx.reply(f"O prefixo neste servidor é: `{utils.getPrefix(ctx)}`")
            else:
                if ctx.author.guild_permissions.administrator:
                    conn, cursor = utils.connectToPrefixDatabase()
                    cursor.execute("INSERT OR REPLACE INTO serverPrefixes (serverID, prefix) VALUES (?, ?)", (ctx.guild.id, new))
                    conn.commit()
                    await ctx.reply(f"O prefixo deste servidor foi modificado para: `{new}`")
                else:
                    await ctx.reply(":x: Você não possui permissões o suficiente para modificar o prefixo deste servidor.")
        except Exception as e:
            await ctx.reply(f"Um erro ocorreu: {e}")

    # Help command: Lists all of Mira's commands.
    @commands.command(aliases = ['ajuda', 'h', 'a'])
    async def help(self, ctx, *, args = ""):
        try:
            helpTextPath = ""
            serverPrefix = utils.getPrefix(ctx)
            helpMessage = ""
            
            if args == "" or args == "--dm":
                helpTextPath = "../text_files/helpMenu.txt"
                helpMessage += f"## Ajuda Mira\n**Prefixo:** `{serverPrefix}`\nDigite `{serverPrefix}ajuda [categoria]` para ver cada categoria em mais detalhes.\n\n" 
            else:
                if "utilidade" in args.lower():
                    helpTextPath = "../text_files/helpUtility.txt"
                    
                elif "rpg" in args.lower():
                    helpTextPath = "../text_files/helpRPG.txt"
                    
                elif "misc" in args.lower():
                    helpTextPath = "../text_files/helpMisc.txt"
                    
                else:
                    helpTextPath = "../text_files/helpError.txt"
                    
                helpMessage = f"## Lista de comandos\n**Prefixo**: `{serverPrefix}`\n"
           
            helpMessage += utils.getTextFromFile(helpTextPath)
        
            if "--dm" in args:
                await ctx.author.send(helpMessage)
                await ctx.reply(f"Mensagem enviada em seu privado, {ctx.author.mention}!")
                return
            
            await ctx.reply(helpMessage)
        
        except Exception as e:
            await ctx.reply(f"Um erro ocorreu: {e}")
            
    # Changelog command: Shows Mira's Latest updates
    @commands.command(aliases = ['cl', 'updates', 'upd'])
    async def changelog(self, ctx, *args):
        message = utils.getTextFromFile("../text_files/changelog.txt")
    
        if "--dm" in args:
            await ctx.author.send(message)
            await ctx.reply(f"Mensagem enviada em seu privado, {ctx.author.mention}!")
            return

        await ctx.reply(message)
    
    # Echo command: Repeats what the user's said.
    @commands.command(aliases = ['eco'])
    async def echo(self, ctx, *, message: str):
        await ctx.reply(message)
    
    # Math command: Returns the result of a mathematical expression
    @commands.command(aliases = ['conta', 'c'])
    async def math(self, ctx, *, expression: str):
        safeChars = "0123456789+-*/() "
        sanitized_expression = ''.join(char for char in expression if char in safeChars)

        try:
            result = eval(sanitized_expression, {'__builtins__': None}, {})
            await ctx.reply(f"Resultado: **{result}**")
        except Exception as e:
            await ctx.reply(f"Erro na expressão: {str(e)}")
        
    
async def setup(bot):
    await bot.add_cog(Utility(bot))
    print("Utility module has finished loading.\n")
