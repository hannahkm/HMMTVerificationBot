#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pickle
import discord
import boto3
from boto3.dynamodb.conditions import Key
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')

dynamodb = boto3.client('dynamodb')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.content.startswith("!verify"):
        await message.channel.send(
            f'Hi {message.author}, welcome to the 2020 HMMT November server! If you are registered for HMMT, you will receive the verified role in the server. If you did not get the role and believe this is a mistake, please DM a moderator!'
        )
        response = dynamodb.query(
            TableName='Discord',
            KeyConditionExpression="DiscordHandle = :name",
            ExpressionAttributeValues={
                ":name": {"S": str(message.author)}
                }
            )
        await message.channel.send(response['Items'])

bot.run(TOKEN)
