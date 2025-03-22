# Library Importing
import discord
from discord.ext import commands
import token
import sqlite3
import os
import asyncio
import modules.utils as utils
from dotenv import load_dotenv

from modules.vanguard.vanguard_db import vanguardInitDatabase

from colorama import init as coloramaINIT
from colorama import Fore
from colorama import Back
from colorama import Style
coloramaINIT()
#-----------------------------------------------------------

# Bot variables setup
load_dotenv(".env")
token: str = os.getenv("DISCORD_TOKEN")
version = "2.1"
intents = discord.Intents.all()
activity = f"Version {version}"

#-----------------------------------------------------------

# Bot instancing
async def getPrefixMain(bot, message):
	return utils.getPrefix(message)

mira = commands.Bot(command_prefix = getPrefixMain, intents=intents)
mira.remove_command("help")
#-----------------------------------------------------------

# Prefixes database connection
dbPath = os.path.join(os.path.dirname(__file__), "modules/prefixes.db")
conn = sqlite3.connect(dbPath)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS serverPrefixes (serverID INTEGER PRIMARY KEY, prefix TEXT)''')
conn.close()

# Vanguard databases initialisation
vanguardInitDatabase()
#-----------------------------------------------------------

# Bot main functions

async def load():
	for filename in os.listdir("./modules"):
		if filename.endswith(".py") and filename.startswith("module-"):
			try:
				print(f"Loading extension: {Fore.RED}{Style.BRIGHT}{filename}...{Style.RESET_ALL}")
				await mira.load_extension(f"modules.{filename[:-3]}")
			except Exception as e:
				print(f"{Fore.RED}Failed to load extension {filename}. Error: {e}{Style.RESET_ALL}")
				await shutdown()

async def shutdown():
	await mira.close()

async def main():
	try:
		if os.name == 'nt':
			os.system("clr")
		else:
			os.system("clear")
			
		await load()
		print(f"{Fore.YELLOW}Logging in...{Style.RESET_ALL}")
		await mira.start(token)
	except KeyboardInterrupt:
		await mira.close()
		await mira.on_disconnect()
	
@mira.event
async def on_ready():
	try:
		if os.name == 'nt':
			os.system("clr")
		else:
			os.system("clear")
		print(f"{Fore.GREEN}Logged in{Style.RESET_ALL} as {Fore.BLUE}{Style.BRIGHT}{mira.user.name}{Style.RESET_ALL}")
		await mira.change_presence(activity=discord.Game(name=activity))
	except Exception as e:
		print(e)

@mira.event
async def on_connect():
	print(f"\nSucessfully connected to Discord.")

@mira.event
async def on_disconnect():
	conn.close()
	print(f"\nSucessfully disconnected from Discord.")
#-----------------------------------------------------------

if __name__ == "__main__":
	loop = asyncio.get_event_loop()

	try:
		loop.run_until_complete(main())
	except KeyboardInterrupt:
		loop.run_until_complete(shutdown())
