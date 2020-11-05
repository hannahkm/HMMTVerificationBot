#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import discord
import boto3
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

dynamodb = boto3.client('dynamodb')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

not_verified_users = set()


@bot.event
async def on_ready():
    members = bot.get_all_members()
    for each_member in members:
        member_roles = list(map(lambda x: x.name, each_member.roles))
        if list(set(member_roles) & set(['Officer', 'Moderator', 'Competitor', 'Auth Bot', 'Censor Bot'])) == []:
            not_verified_users.add(each_member)
    recheck_members.start()


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the 2020 HMMT November server! If you are registered for HMMT, you will receive the verified role in the server. If you did not get the role and believe this is a mistake, please DM a moderator!'
    )
    if verify_member(member):
        role = get(member.guild.roles, name='Competitor')
        await member.add_roles(role)
    else:
        not_verified_users.add(member)
        await member.dm_channel.send("We are not able to verify you at this time. Please enter your discord ID on the HMMO website")


def verify_member(member):
    response = dynamodb.query(
        TableName='Discord',
        KeyConditionExpression="DiscordHandle = :name",
        ExpressionAttributeValues={
            ":name": {"S": str(member.name) + "#" + str(member.discriminator)}
            }
        )
    if response['Items'] != [] and response['Items'][0]['Approved']['BOOL']:
        return True
    else:
        return False


@tasks.loop(seconds=3600)
async def recheck_members():
    if len(not_verified_users) > 0:
        for each_member in not_verified_users:
            if verify_member(each_member):
                role = get(each_member.guild.roles, name='Competitor')
                await each_member.add_roles(role)


bot.run(TOKEN)
