# Library Importing
import discord
from discord.ext import commands
import modules.utils as utils
import modules.dice_parser as parser
import re
import random

from colorama import init as coloramaINIT
from colorama import Fore
from colorama import Style
coloramaINIT()
#-----------------------------------------------------------

class RPG(commands.Cog):

	# Constructor
	def __init__(self, bot):
		self.bot = bot
	
	@commands.Cog.listener()
	async def on_ready(self):
		print(f"RPG cog listener is {Fore.GREEN}ready{Style.RESET_ALL}.")
		
	#-------------------------------------------------------

	# Dice roll command: rolls any number of any type of dice
	@commands.command(aliases = ['r'])
	async def roll(self, ctx, *, expression: str):
		try:
			total, details = parser.parseExpression(expression)
			response = (
				f"Dados: {', '.join(details)}\n"
				f"Total: {total}"
			)

			# Split the response into chunks of 2000 characters or less
			if len(response) > 2000:
				chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
				for chunk in chunks:
					await ctx.send(chunk)
			else:
				await ctx.send(response)
		except Exception as e:
			await ctx.reply(f"Um erro ocorreu: {e}")
	
async def setup(bot):
	await bot.add_cog(RPG(bot))
	print("RPG module has finished loading.\n")
