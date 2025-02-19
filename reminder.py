import discord
import os # default module
from dotenv import load_dotenv
from discord.commands import Option
from discord.ext import commands, tasks
import requests
from discord import Webhook
import random

#To add:
#Creating/deleting characters and adding/removing them to the pool and data.txt
#Giving custom colors as an option
#Updating different information and saving them to data.txt while running
#Add multiple possible lines for characters

load_dotenv() # load all the variables from the env file
bot = discord.Bot()
reminder_channel = None
started = False
people = []
webhook = None
last_num = None

@bot.event
async def on_ready():
    text = open("data.txt")
    num_people = int(text.readline())
    global people
    people = [dict() for _ in range(num_people)]
    total = 0

    for x in range(num_people):
        pfp = text.readline()
        name = text.readline()
        image = text.readline()
        message = text.readline()
        weight = float(text.readline())
        people[x] = {'pfp': pfp, 'name': name, 'image': image, 'message': message, 'weight': weight}
        total += weight

    for x in range(num_people):
        people[x]['weight'] = people[x]['weight']/total
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="setchannel", description="Set the bot to send messages in this channel, or a specified channel")
@commands.has_permissions(manage_messages=True)
async def setchannel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    global reminder_channel
    reminder_channel = channel
    webhooks = await reminder_channel.webhooks()
    global webhook
    found_web = False
    for check_webhook in webhooks:
        if check_webhook.name == "Webhook Bot":
            webhook = check_webhook
            found_web = True
    if not found_web:
        webhook = await reminder_channel.create_webhook(name = "Webhook Bot")
    await ctx.respond("Set Channel Successfully", ephemeral = True)

@bot.slash_command(name="send", description="Send a message to the set channel")
@commands.has_permissions(manage_messages=True)
async def send(ctx: discord.ApplicationContext, message):
    if not message:
        await ctx.respond("Messaged failed to send, did you set a message?", ephemeral = True)
    elif not reminder_channel:
        await ctx.respond("Channel not set yet, please use /setchannel.", ephemeral = True)
    else:
        await reminder_channel.send(message)
        await ctx.respond("Sent Message Successfully", ephemeral = True)

@tasks.loop(minutes = 1)
async def remind():
    if started:
        global webhook
        global people
        embeded = discord.Embed(colour = 0xE4A8CA)
        num = random.uniform(0, 1)
        print(num)
        chosen_person = "meow"
        for character in people:
            if num - character['weight'] < 0:
                chosen_person = character
                break
            else:
                num -= character['weight']
                print("try again " + str(num))
        value = chosen_person
        embeded.set_image(url = value['image'])
        embeded.add_field(name = "REFILL REMINDER!! ", value = value['message'])
        embeded.set_thumbnail(url = value['pfp'])
        await webhook.send(embed = embeded, avatar_url = value['pfp'], username = value['name'])

@bot.slash_command(name="settime", description="Set the bot's refill reminder to a certain amount of minutes")
@commands.has_permissions(manage_messages=True)
async def settime(ctx: discord.ApplicationContext, time):
    remind.change_interval(minutes = int(time))
    await ctx.respond("Set Channel Successfully", ephemeral = True)

@bot.slash_command(name="startstop", description="Start/Stop the bot.")
@commands.has_permissions(manage_messages=True)
async def startstop(ctx: discord.ApplicationContext):
    global started
    started = not started
    if started and reminder_channel == None:
        started = False
        await ctx.respond("Channel not set yet, please use /setchannel.", ephemeral = True)
    elif started:
        remind.start()
        await ctx.respond("Successful, started up.", ephemeral = True)
    else:
        remind.cancel()
        await ctx.respond("Successful, stopped.", ephemeral = True)

@bot.slash_command(name="list", description="List out all of the possible refill reminders.")
@commands.has_permissions(manage_messages=True)
async def list(ctx: discord.ApplicationContext):
    global webhook
    global people
    for character in people:
        char = character
        embeded = discord.Embed(colour = 0xE4A8CA)
        embeded.set_image(url = char['image'])
        embeded.add_field(name = "REFILL REMINDER!! ", value = char['message'])
        embeded.set_thumbnail(url = char['pfp'])
        await webhook.send(embed = embeded, avatar_url = char['pfp'], username = char['name'])


bot.run(os.getenv('TOKEN'))