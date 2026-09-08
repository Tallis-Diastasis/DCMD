import discord
from os import getenv
from dotenv import load_dotenv
import subprocess as subp
import threading
import asyncio
load_dotenv()

class Client(discord.Client):
	async def on_ready(self):
		print(f"Logged on as {self.user}.")

	async def on_message(self, message):
		if message.author.name in ["DCMD", "cootshk"]: return
		if str(message.channel.id) != getenv("CHANNEL_ID"): return
		msg = message.content
		if msg[0] == "$": return
		if msg == "help":
			await message.reply("It's quite simple really.\nAny message you send will be interpreted as a bash command and be piped into an instance of Arch Linux.\nWhen you send a message, this bot will reply with [n] which is the return code. The return code is the status of the command - Did it succeed (0) or failed (any other number).\n\nYou can use any bash command. What else? I guess \"you have root\" or something?\nK. Bye.")
			return
		threading.Thread(target=self.run_command, args=(message, msg), daemon=True).start()

	def run_command(self, message, msg):
		out = ""
		debug = False
		if msg[0] == "!": msg = msg[1:]; debug = True
		if msg.startswith("```"):
			msg = msg[3:-3]
			out = []
			lines = [l for l in msg.split("\n") if l]
			for l in lines:		
				result = subp.run(l, shell=True, capture_output=True, text=True)
				out.append(f"[{str(result.returncode)}]\n" + result.stdout.strip() + result.stderr)
			out = "\n".join(out)
		else:
			result = subp.run(msg, shell=True, capture_output=True, text=True)
			out = f"[{str(result.returncode)}]\n" + result.stdout + result.stderr
		out = out.replace("`", "\\`")
		if len(out) > 2000:
			num = len(out[2000:])
			numstr = f"... Plus {num} more characters."
			out = out[:2000-len(numstr)] + numstr

		asyncio.run_coroutine_threadsafe(message.channel.send(content="```ANSI\n"+out+"```", reference=message, mention_author=False), self.loop)

TOKEN = getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = Client(intents=intents)
bot.run(TOKEN)
