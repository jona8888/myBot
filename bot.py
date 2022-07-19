# bot.py

import os
import discord
import random
import requests
import re
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
from dotenv import load_dotenv
from discord import Color

import discord


load_dotenv()
TOKEN = 'replace with Your bot token here'
GUILD = 'replace with you Guild here'


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!')
        

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.command(name='guess')
async def nine_nine(ctx):
    
    print('guess number between 1-10')
    brooklyn_99_quotes = [
        '1','2','3','4','5','6','7','8','9','10'
    ]
    
    
    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    



api_key = "da0812526696b2dd99ebe393eb61f1e2"
w_addy = "http://api.openweathermap.org/data/2.5/weather?"

@bot.command()
async def weather(ctx, *, city: str):


    metro = city
    real_addy = w_addy + "appid=" + api_key + "&q=" + metro
    response = requests.get(real_addy)
    x = response.json()
    channel = ctx.message.channel


    if x["cod"] != "404":
        async with channel.typing():


            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = round(current_temperature - 273.15)
            current_temperature_far = round((current_temperature_celsiuis * 1.8) + 32)
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]


            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {metro}",
                              color=ctx.guild.me.top_role.color,
                              timestamp=ctx.message.created_at,)
            embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Temperature(F)", value=f"**{current_temperature_far}°F**", inline=False)
            embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")


        await channel.send(embed=embed)
    else:
        await channel.send("City not found.")



# disable default help
bot.remove_command('help')

# -------------------

# check if a role is not being used, and delete it
# this waits a bit before checking since discord
# likes to take some time before reporting changes
async def snooze_move(part):
    await asyncio.sleep(10) # give time before checking
    return await look_move(part)

# this is only called directly from the purge command
async def look_move(part):
    if len(part.members) == 0:
        await part.delete()
        return True
    return False

# use requests to query the colourlovers API
async def color_lover_api(keywords):
    keywords = keywords.replace(" ", "+") # they use + instead of %20
    url = f"http://www.colourlovers.com/api/colors?keywords={keywords}&numResults=1&format=json"
    top = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    hexcode = "#" + requests.get(url, headers=top).json()[0]["hex"] # fancy
    return hexcode

# remove colors, returns the number of 
# roles removed from the specified user
# (generally 1 but jic one gets stuck)
async def remove_colors(ctx, author):
    color_roles = []
    color_again = re.compile(r'^\#[0-9A-F]{6}$')
    for role in author.roles:
        # only remove color roles
        if color_again.match(role.name.upper()):
            color_roles.append(role)

    # once all the roles are collected,
    # remove them from the user
    for part in color_roles:
        await author.remove_roles(role)
        # if the role is no longer being used,
        # delete it. run it async as there's 
        # a 10 second (or so) wait in the check
        asyncio.create_task(snooze_move(part))

    return len(color_roles)

# simple source command
@bot.command()
async def source(ctx):
    await ctx.send("blep <https://github.com/Savestate2A03/SimpleDiscordColorBot>")

# simple help command
@bot.command()
async def help(ctx):
    await ctx.send("choose a color here : "
        "<https://htmlcolorcodes.com/color-picker/>, and run the command \n"
        "`!color #RRGGBB` where '#RRGGBB' is the hex code you want !\n"
        "You can also use general descriptions of colors (ex: `!color dark purple`) \n"
        "For weather forecast in you area, type `!weather YourCityHere` (ex: '!weather Boston') ")

@bot.command(name="color", aliases=["colour"])
async def color(ctx, *color):
    # if the command is improperly
    # formatted, invoke help and exit
    if len(color) == 0:
        await help.invoke(ctx)
        return

    message = ctx.message
    author  = message.author 
    guild   = message.guild
    color_lover = False # flag if used the colourlovers API

    color = " ".join(color)
    color = color.upper() # makes things easier

    if color == "REMOVE":
        # see if any roles were removed
        # and let the user know how the removal
        # process went.
        removed = await remove_colors(ctx, author)
        if removed > 0:
            await ctx.send("color vaporized !")
        else:
            await ctx.send("no color role to remove !")
        return

    # look for hex code match
    re_color = re.compile(r'^\#[0-9A-F]{6}$')
    if not re_color.match(color):
        # if not a hex code, use colourlovers API
        color_lover = True 
        color = await color_lover_api(color)

    # remove all color roles in preperation
    # for a new color role
    await remove_colors(ctx, author)

    assigned_role = None

    # check if the role already exists. if 
    # it does, assign that instead of 
    # making a new role
    for role in guild.roles:
        if role.name.upper() == color:
            assigned_role = role

    # if we didn't find the role, make it
    if assigned_role == None:
        red   = int(color[1:3], 16) #.RR....
        green = int(color[3:5], 16) #...GG..
        blue  = int(color[5:7], 16) #.....BB
        assigned_role = await guild.create_role(
            name=color, 
            color=discord.Color.from_rgb(red, green, blue))

    # assign the role we found/created
    await author.add_roles(assigned_role)

    await ctx.send(f"colorized !")

# remove colors that somehow dont get deleted
@bot.command()
async def purge(ctx):
    note = ctx.note
    writer  = note.writer 
    guild   = note.guild
    allowed = writer.guild_permissions.manage_roles

    if not allowed:
        await ctx.send("you can't manage roles !")
        return

    # discord throttles a lot of stuff here
    # so going through all the roles takes a little while
    await ctx.send(f"purging unassigned colors ! ... this may take a sec ...")

    color_again = re.compile(r'^\#[0-9A-F]{6}$')
    num_deleted = 0

    roles = guild.roles
    progress = await ctx.send(f"progress: 0/{len(roles)}")
    iterations = 0

    for part in roles:
        if color_again.match(part.name): # if a color role
            deleted = await look_move(part)
            if deleted:
                num_deleted += 1
        iterations += 1
        # edit our previous progress message (fancy)
        await progress.edit(content="progress: "
                f"{iterations}/{len(roles)}")

    # final report
    await ctx.send(f"removed {num_deleted} unassigned colors !")

# -------------------

# read token from token.txt
token = "womp"
with open('coin.txt', 'r') as file:
    token = file.read().replace('\n', '')



bot.run(TOKEN)
