#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pickle
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
#client = discord.Client()

values_input = []

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

@bot.command(
	help="Use !setup [SHEETS ID] [COLUMN] to connect a Google Spreadsheet.",
	brief="Connect a Google Spreadsheet to use"
)
async def setup(ctx, *args, message):
    global values_input, service
    if "moderator" in [y.id for y in message.author.roles]:
        sheetID, col = args
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)  # here enter the name of your downloaded JSON file
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=sheetID,range=col).execute()
        values_input = result_input.get('values', [])

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.event
async def on_member_join(member):
    global values_input
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the 2020 HMMT November server! If you are registered for HMMT, you will receive the verified role in the server. If you did not get the role and believe this is a mistake, please DM a moderator!'
    )
    username = member.name + "#" + member.discriminator
    if ([username] in values_input):
        role = get(member.guild.roles, name="verified")
        await member.add_roles(role)


#client.run(TOKEN)
bot.run(TOKEN)
