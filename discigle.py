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
reveal_requests = {}   


@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        await member.send("Thank you for using our bot! Type `!find` to start chatting.")
    except discord.Forbidden:
        print(f"Could not send a message to {member}")

@bot.command()
async def find(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        if user in active_chats:
            await user.send("You're already in a chat! Type `!stop` or `!next` to leave.")
            return

        if user in queue:
            await user.send("You're already in the queue!")
            return

        queue.append(user)
        await user.send("Searching for a stranger...")

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
            stranger = active_chats.pop(user, None)

            if stranger and stranger in active_chats:
                active_chats.pop(stranger, None)
                await stranger.send("Your chat stranger has left. Type `!find` to find a new stranger.")

            await user.send("Chat ended. Type `!find` to find a new stranger.")
        else:
            await user.send("You're not in a chat!")


@bot.command()
async def next(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        if user in active_chats:
            stranger = active_chats.pop(user, None)

            if stranger and stranger in active_chats:
                active_chats.pop(stranger, None)
                await stranger.send("Your chat stranger skipped. Type `!find` to find a new stranger.")

            await user.send("You skipped the chat. Finding a new stranger...")

            queue.append(user)

            if len(queue) >= 2:
                user1 = queue.pop(0)
                user2 = queue.pop(0)
                active_chats[user1] = user2
                active_chats[user2] = user1

                await user1.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")
                await user2.send("You're now connected! Type messages to chat. Type `!stop` to end or `!next` to switch.")
        else:
            await user.send("You're not in a chat. Type `!find` to start!")


@bot.command()
async def reveal(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        user = ctx.author
        if user in active_chats:
            stranger = active_chats[user]
            reveal_requests[user] = True
            
            if stranger in reveal_requests:
                await user.send(f"Your chat stranger's Discord: {stranger.name}#{stranger.discriminator}")
                await stranger.send(f"Your chat stranger's Discord: {user.name}#{user.discriminator}")
                
                reveal_requests.pop(user, None)
                reveal_requests.pop(stranger, None)
            else:
                await user.send("Reveal request sent! Waiting for your stranger to type `!reveal` as well.")
        else:
            await user.send("You're not in a chat! Type `!find` to start.")


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        user = message.author
        if user in active_chats:
            stranger = active_chats[user]
            embed = discord.Embed(title="New Message", description=message.content, color=discord.Color.blue())
            embed.set_footer(text="Stranger")
            await stranger.send(embed=embed)
        elif message.content.startswith("!"):
            await bot.process_commands(message) 
        else:
            await user.send("You're not in a chat. Type `!find` to start!")


bot.run(TOKEN)
