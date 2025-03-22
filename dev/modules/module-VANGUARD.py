import discord
from discord.ext import commands
import asyncio

from .vanguard import vanguard_dataclasses
from .vanguard.vanguard_db import *
from .utils import getPrefix

from colorama import init as coloramaINIT
from colorama import Fore
from colorama import Style
coloramaINIT()
#-----------------------------------------------------------

class Vanguard(commands.Cog):
	# Constructor
	def __init__(self, bot):
		self.bot = bot
		self.vanguards = {}
				
	@commands.Cog.listener()
	async def on_ready(self):

		print(f"Vanguard cog listener is {Fore.GREEN}ready{Style.RESET_ALL}.")

	#-------------------------------------------------------

	async def createVanguardThread(self, ctx: commands.Context) -> discord.Thread:
		try:
			thread = await ctx.channel.create_thread(
				name=f"Vanguard - {ctx.author.display_name}",
				type=discord.ChannelType.public_thread,
				auto_archive_duration=60,
				reason=f"Partida iniciada por {ctx.author.display_name}"
			)

			await thread.add_user(ctx.author)

			self.vanguards[ctx.author.id] = thread.id

			return thread
		except Exception as e:
			await ctx.reply(f"Ocorreu um erro ao criar a partida: {e}")

	async def characterCreation(self, ctx, author):
		await ctx.send(f"Bem-vindo ao Vanguard, {author.mention}! Você ainda não tem um personagem - Que tal criarmos um? :sparkles::shield:\nPodemos começar com o nome do seu personagem. Como você irá se chamar?")

		def check(m):
			return m.author == author and m.channel == ctx

		try:
			# Step 1: Get character name
			msg = await self.bot.wait_for('message', check=check, timeout=30)
			characterName = msg.content
			
			# Step 2: Assign modifiers to stats
			modifiers = [-2, -1, 0, +1, +2]
			stats = ["Força", "Fineza", "Vitalidade", "Feitiçaria", "Velocidade"]
			assignedStats = {}

			await ctx.send(f"Agora, você deve atribuir os modificadores {modifiers} aos seguintes atributos: {', '.join(stats)}.\nVamos fazer isso um de cada vez. Por favor, responda com o número correspondente ao modificador para cada atributo.")

			for stat in stats:
				await ctx.send(f"Escolha um modificador para {stat}. Modificadores restantes: {modifiers}")

				def statCheck(m):
					return (
						m.author == author 
						and m.channel == ctx 
						and (m.content.isdigit() or (m.content[0] in ['+', '-'] and m.content[1:].isdigit()))
					)
				try:
					msg = await self.bot.wait_for('message', check=statCheck, timeout=30)
					modifier = int(msg.content)
					assignedStats[stat] = modifier
					modifiers.remove(modifier)
				except asyncio.TimeoutError:
					await ctx.send(f"Você demorou demais para responder. Tente novamente com `{getPrefix(ctx)}character`!")
					return

			strength, finesse, vitality, spellcasting, speed = [assignedStats[stat] for stat in stats]

			
			# Step 3: Create Character and Attributes
			attributes = Attributes(strength=strength, finesse=finesse, vitality=vitality, spellcasting=spellcasting, speed=speed)
			character = Character(name=characterName, level=1, exp=0, attributes=attributes)

			# Step 4: Create Player and Insert into Database
			newPlayer = Player(username=author.name, ID=author.id, character=character)
			vanguardInsertPlayer(newPlayer)  # Insert the player and character into the database

			await ctx.send(f"Parabéns, {author.mention}! Seu personagem {characterName} foi criado com sucesso! Tente usar `{getPrefix(ctx)}character` para ver a sua ficha de personagem!")
		
		except asyncio.TimeoutError:
			await ctx.send(f"Você demorou demais para responder, {author.mention}. Por favor, tente novamente mais tarde.")

	@commands.command()
	async def vanguard(self, ctx):
		try:
			if not isinstance(ctx.channel, discord.TextChannel):
				await ctx.reply("Este comando só pode ser usado em um canal de texto padrão!")
				return

			if ctx.author.id in self.vanguards:
				await ctx.reply(f"Você já está em uma partida de Vanguard! Retorne para <#{self.vanguards.get(ctx.author.id)}>, ou feche-a com o comando `{getPrefix(ctx)}exit` antes de iniciar outra!")
				return

			await ctx.reply("Estou criando uma Thread com sua partida de Vanguard!")
			thread = await self.createVanguardThread(ctx)

			if not vanguardPlayerExists(ctx.author.id):
				try:
					await self.characterCreation(thread, ctx.author)
				except Exception as e:
					await thread.send(f"{e}")
			else:
				await thread.send(f"Bem vindo de volta ao Vanguard, {ctx.author.mention}!")
		except Exception as e:
			await ctx.reply(e)

	@commands.command(aliases = ['char'])
	async def character(self, ctx):
		if not vanguardPlayerExists(ctx.author.id):
			await self.characterCreation(ctx, ctx.author)
			return

		player = vanguardGetPlayer(ctx.author.id)
		character = player.character

		# Create a character sheet
		character_sheet = (
			f"**Nome:** {character.name}\n"
			f"**Nível:** {character.level}\n"
			f"**Experiência:** {character.exp}\n\n"
			f"**Atributos:**\n"
			f"- Força: {character.attributes.strength}\n"
			f"- Fineza: {character.attributes.finesse}\n"
			f"- Vitalidade: {character.attributes.vitality}\n"
			f"- Feitiçaria: {character.attributes.spellcasting}\n"
			f"- Velocidade: {character.attributes.speed}\n"
		)

		await ctx.send(f"Aqui está a sua ficha de personagem:\n{character_sheet}")

	@commands.command()
	async def exit(self, ctx):
		threadID = self.vanguards.get(ctx.author.id)

		if threadID is None:
			await ctx.reply("Você não está em uma partida de Vanguard!")
			return

		thread = self.bot.get_channel(threadID)

		if isinstance(thread, discord.Thread) and thread.owner_id == self.bot.user.id:
			try:
				await thread.delete()
				del self.vanguards[ctx.author.id]
				await ctx.send(f"Partida finalizada, {ctx.author.mention}!")
			except Exception as e:
				await ctx.reply(f"Ocorreu um erro ao tentar finalizar a partida: {e}")
		else:
			await ctx.reply("Você não pode sair dessa Thread, ela não foi criada por mim!")

async def setup(bot):
	await bot.add_cog(Vanguard(bot))
	print("Vanguard module has finished loading.\n")