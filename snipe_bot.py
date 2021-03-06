#! /usr/bin/python3

# Usage $<track/untrack> <CRN>

import discord, asyncio, aiohttp
from oscar_scraper import *
from discord.ext import commands, tasks


def add_class(user, crn):
    """
    Precondition: crn is validated
    """ 
    if crn in tracking and user not in tracking[crn]:
        tracking[crn].append(user)
    else:
        tracking[crn] = [user]
    

def remove_class(user, crn):
    tracking[crn].remove(user)
    if len(tracking[crn]) == 0:
        del tracking[crn]

tracking = {}
current_class_status = {}

client = commands.Bot(command_prefix='$')


@client.event
async def on_ready():
    check_status_and_notify.start()


@client.command()
async def track(ctx, crn):
    try:
        reg_data = await scrape(crn)
        status = await class_status(reg_data)
        add_class(ctx.author, crn)
        current_class_status[crn] = status
        await ctx.send(f'{ctx.author.mention} Now tracking {crn}.')
    except:
        await ctx.send(f'{ctx.author.mention} Could not find class with CRN: {crn}.')


@client.command()
async def untrack(ctx, crn):
    if crn in tracking and ctx.author in tracking[crn]:
        remove_class(ctx.author, crn)
        await ctx.send(f'{ctx.author.mention} Stopped tracking {crn}.')
    else:
        await ctx.send(f'{ctx.author.mention} You are not tracking {crn}. Did you mean "track"?')


async def check_for_status_changes():
    changed_status = {}
    for crn in tracking:
        status = class_status(scrape(crn))
        if status != current_class_status[crn]:
            changed_status[crn] = current_class_status[crn]
            current_class_status[crn] = status
    return changed_status


@tasks.loop(minutes=1.0)
async def check_status_and_notify():
    changed_status = await check_for_status_changes()
    for crn in changed_status:
        for user in tracking[crn]:
            await user.send('Class %s changed from %s to %s.' % (crn,
                      changed_status[crn], current_class_status[crn]))


client.run('token')


# TODO: Automatically untrack after 72 hours.
# TODO: 4 course limit per person.
