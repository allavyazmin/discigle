import discord
import random
from discord.ext import commands

TOKEN = ""

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []  
active_chats = {}  


@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")


@bot.command()
async def find(ctx):
    """User enters the queue to find a chat partner."""
    if isinstance(ctx.channel, discord.DMChannel):  
        user = ctx.author
        if user in active_chats:
            await user.send("You're already in a chat! Type `!stop` or `!next` to leave.")
            return

        if user in queue:
            await user.send("You're already in the queue!")
            return

        queue.append(user)
        await user.send("Searching for a partner...")

        if len(queue) >= 2:
            user1 = queue.pop(0)
            user2 = queue.pop(0)
            active_chats[user1] = user2
            active_chats[user2] = user1

            await user1.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")
            await user2.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")


@bot.command()
async def stop(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        if user in active_chats:
            partner = active_chats.pop(user, None)

            # If the partner exists, remove their connection too
            if partner and partner in active_chats:
                active_chats.pop(partner, None)
                await partner.send("Your chat partner has left. Type `!find` to find a new partner.")

            await user.send("Chat ended. Type `!find` to find a new partner.")
        else:
            await user.send("You're not in a chat!")


@bot.command()
async def next(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        if user in active_chats:
            partner = active_chats.pop(user, None)

            # If the partner exists, remove their connection too
            if partner and partner in active_chats:
                active_chats.pop(partner, None)
                await partner.send("Your chat partner skipped. Type `!find` to find a new partner.")

            await user.send("You skipped the chat. Finding a new partner...")

            # Add the user back to the queue
            queue.append(user)

            # Try to match with a new partner
            if len(queue) >= 2:
                user1 = queue.pop(0)
                user2 = queue.pop(0)
                active_chats[user1] = user2
                active_chats[user2] = user1

                await user1.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")
                await user2.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")
        else:
            await user.send("You're not in a chat. Type `!find` to start!")


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        user = message.author
        if user in active_chats:
            partner = active_chats[user]
            await partner.send(f"Stranger: {message.content}")
        elif message.content.startswith("!"):
            await bot.process_commands(message)  # Allow commands
        else:
            await user.send("You're not in a chat. Type `!find` to start!")


bot.run(TOKEN)
