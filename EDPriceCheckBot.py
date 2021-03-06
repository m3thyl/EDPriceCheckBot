#!/usr/bin/python3 -u

import os
import re
import discord
import asyncio
from datetime import datetime
#Logging stuff for when stuff just stops working
#import logging
#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

class EDPriceCheckBot(discord.Client):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.launch = 0
        self.memberset = set()
        self.dmset = set()
        self.timeoutlst = []
        self.timeoutdict = {}
        self.tokenfile = open('token','r')
        self.TOKEN = self.tokenfile.readline().rstrip()
        self.botadminfile = open('botadmin','r')
        self.botadmin = int(self.botadminfile.readline().rstrip())
        self.bgtask1 = self.loop.create_task(self.price_watcher())

    def price_grabber(self,commodity):
        if commodity.lower() == 'ltd' or commodity.lower() == 'ltds':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('lowtemperaturediamond')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'vopals' or commodity.lower() == 'void opals':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('opal')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'vopal' or commodity.lower() == 'void opal':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('opal')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'painite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('painite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'benitoite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('benitoite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'musgravite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('musgravite') 
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'grandidierite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('grandidierite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        elif commodity.lower() == 'serendibite':
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.cmdty_reader('serendibite')
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst
        else:
            stationlst = []
            systemlst = []
            pricelst = []
            demandlst = []
            padsizelst = []
            agelst = []
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst

    def cmdty_reader(self,cmdty):
        stationlst = []
        systemlst = []
        pricelst = []
        demandlst = []
        padsizelst = []
        agelst = []
        with open(cmdty) as f:
            lines = f.readlines()
            for line in lines:
                linesplit = line.split(',')
                stationlst.append(linesplit[0])
                systemlst.append(linesplit[1])
                pricelst.append('{:,}'.format(int(linesplit[2])))
                demandlst.append('{:,}'.format(int(linesplit[3])))
                padsizelst.append(linesplit[4])
                agelst.append(linesplit[5])
            return stationlst,systemlst,pricelst,demandlst,padsizelst,agelst

    def file_create_check(self):
        if not os.path.exists('membership.lst'):
            print('Generating membership.lst')
            os.mknod('membership.lst')
        if not os.path.exists('dm.lst'):
            print('Generating dm.lst')
            os.mknod('dm.lst')

    def memberset_gen(self):
        memberfile = open('membership.lst','r')
        for member in memberfile.readlines():
            self.memberset.add(member.rstrip())
        memberfile.close()

    def alertset_gen(self):
        dmfile = open('dm.lst','r')
        for user in dmfile.readlines():
            self.dmset.add(user.rstrip())
        dmfile.close()

    def member_write(self,guildid,channelid):
        memberfile = open('membership.lst','a')
        memberfile.write(str(guildid) + ',' + str(channelid) + '\n')
        memberfile.close()
        self.memberset_gen()

    def alert_write(self,user):
        dmfile = open('dm.lst','a')
        dmfile.write(str(user.id) + '\n')
        dmfile.close()
        self.alertset_gen()

    def alert_delete(self,user):
        with open('dm.lst','r') as f:
            lines = f.readlines()
        with open('dm.lst','w') as f:
            for line in lines:
                if not str(user.id) in line.strip('\n'):
                    f.write(line)
        self.dmset = set()
        self.alertset_gen()

    def set_channel_check(self,channelid,guildid):
        memberid = str(guildid) + ',' + str(channelid)
        for entry in self.memberset:
            guildsplit = entry.split(',')
            if str(guildid) in guildsplit[0]:
                return False
        if not memberid in self.memberset:
            return True

    def member_delete(self,target):
        with open('membership.lst','r') as f:
            lines = f.readlines()
        with open('membership.lst','w') as f:
            for line in lines:
                if not str(target.id) in line.strip('\n'):
                    f.write(line)
        self.memberset = set()
        self.memberset_gen()

    def channel_delete(self,channel):
        with open('membership.lst','r') as f:
            lines = f.readlines()
        with open('membership.lst','w') as f:
            for line in lines:
                if not str(channel) in line.strip('\n'):
                    f.write(line)
        self.memberset = set()
        self.memberset_gen()

    def dm_delete(self,user):
        with open('membership.lst','r') as f:
            lines = f.readlines()
        with open('membership.lst','w') as f:
            for line in lines:
                if not str(user) in line.strip('\n'):
                    f.write(line)
        self.dmset = set()
        self.alertset_gen()

    def unset_channel(self,messagechannel):
        self.member_delete(messagechannel)

    def alert_checker(self):
        i = 0
        stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.price_grabber('ltd')
        idescription = ''
        while i < 5:
            price = pricelst[i].replace(',','')
            if int(price) >= 1500000:
                demand = demandlst[i].replace(',','')
                if int(demand) >= 2000:
                    if not stationlst[i] in self.timeoutlst:
                        print(stationlst[i] + ', ' + systemlst[i] + " has high LTD sell price!")
                        self.timeoutlst.append(stationlst[i])
                        idescription+='\n**' + stationlst[i] + ', ' + systemlst[i] + '**\n'
                        idescription+='Sell price: **' + pricelst[i] + '**\n'
                        idescription+='Demand: **' + demandlst[i] + '**\n'
                        idescription+='Pad size: **' + padsizelst[i] + '**\n'
                        idescription+='Time since last update: **' + agelst[i] + '**'
            i += 1
        if not idescription == '':
            ititle = '**High LTD price alert!**'
            em = discord.Embed(
                title=ititle,
                description=idescription,
                color=0x00FF00
            )
            return em
        else:
            em = None
            return em

    def timeout_checker(self):
        if self.timeoutlst:
            for entry in self.timeoutlst:
                if not entry in self.timeoutdict:
                    self.timeoutdict[entry] = datetime.now()
                else:
                    timediff = datetime.now() - self.timeoutdict[entry]
                    if int(timediff.total_seconds()) >= 86400:
                        print("Timeout reached for " + entry)
                        del self.timeoutdict[entry]
                        self.timeoutlst.remove(entry)

    async def price_watcher(self):
        i = 0
        await self.wait_until_ready()
        print('Starting price watcher')
        while not self.is_closed():
            if self.launch == 0:
                self.launch = 1
                await asyncio.sleep(1)
            else:
                em = self.alert_checker()
                if em is not None:
                    for userid in self.dmset:
                        user = self.get_user(int(userid))
                        if not user is None:
                            print("Sending alert to user " + str(userid))
                            await user.send(embed=em)
                            await asyncio.sleep(1)
                        else:
                            print("Deleting invalid user " + str(userid))
                            self.dm_delete(userid)
                    for member in self.memberset:
                        channelsplit = member.split(',')
                        channel = self.get_channel(int(channelsplit[1]))
                        if not channel is None:
                            print("Sending alert to channel")
                            await channel.send(embed=em)
                            await asyncio.sleep(1)
                        else:
                            print("Deleting invalid channel " + str(member))
                            self.channel_delete(channelsplit[1])
                    print("Done sending alerts to users")
                    self.timeout_checker()
                    await asyncio.sleep(1)
                else:
                    self.timeout_checker()
                    await asyncio.sleep(1)

    async def on_guild_channel_delete(self,channel):
        print("Bot removed from channel " + str(channel))
        self.member_delete(channel)

    async def on_guild_remove(self,guild):
        print("Bot removed from server " + str(guild))
        self.member_delete(guild)

    async def on_message(self,message):
        #Make sure message.guild is not NoneType and create var for checking against memberset
        if message.guild is None:
            return
        else:
            memberid = str(message.guild.id) + ',' + str(message.channel.id)

        #Don't reply to yourself
        if message.author == self.user:
            return

        #Reload DM and Membership sets as long as it's from the bot owner
        if message.content.startswith('!reloadsets'):
            if message.author.id == self.botadmin:
                self.alertset_gen()
                self.memberset_gen()
                print("Both sets regenerated")

        #Set primary channel
        if message.content.startswith('!setchannel'):
            result = self.set_channel_check(message.channel.id,message.guild.id)
            if result == True:
                self.member_write(message.guild.id, message.channel.id)
                await message.channel.send('Channel set.')
            else:
                await message.channel.send('Channel already set, please run `!unsetchannel` in the currently set channel before running this command again.')

        #Only allow calls from channels in the membership set
        if not memberid in self.memberset:
            return

        #Help response
        if message.content.startswith('!help'):
            em = discord.Embed(
                title='EDPriceAlert Help',
                description="""Available Commands:
                            `!help`
                            Displays this help message
                            `!setchannel`
                            Sets primary channel for price alerts and communication based on where the command is executed
                            `!unsetchannel`
                            Unsets primary channel (Must be run in the currently assigned primary channel)
                            `!check x`
                            Checks top 5 mineral prices where x is the name of the mineral
                            `!getalerts`
                            Sends DM to user when prices for LTD's reach 1.5mil with at least 2000 demand
                            `!stopalerts`
                            Removes user from DM list
                            """,
                color=0x00FF00
            )
            await message.channel.send(embed=em)

        #Unset primary channel
        if message.content.startswith('!unsetchannel'):
            await message.channel.send('Are you sure you want to unset this channel as the primary channel? (y/n)')
            try:
                msg = (await self.wait_for('message',timeout=30.0)).content
                if msg.lower()[0] == 'y':
                    self.unset_channel(message.channel)
                    await message.channel.send('Channel unset, use `!setchannel` to set a new primary channel.')
                elif msg.lower()[0] == 'n':
                    await message.channel.send('Channel preferences have not been changed.')
                else:
                    await message.channel.send('Unrecognized input, preferences have not been changed.')
            except asyncio.TimeoutError:
                await message.channel.send('Timed out, channel has not been modified.')

        #Mineral check
        if message.content.startswith('!check'):
            content = re.split('!check ', message.content)[-1]
            stationlst,systemlst,pricelst,demandlst,padsizelst,agelst = self.price_grabber(content)
            if stationlst:
                i = 0
                idescription = ''
                while i < 5:
                    idescription+='\n**' + stationlst[i] + ', ' + systemlst[i] + '**\n'
                    idescription+='Sell price: **' + pricelst[i] + '**\n'
                    idescription+='Demand: **' + demandlst[i] + '**\n'
                    idescription+='Pad size: **' + padsizelst[i] + '**\n'
                    idescription+='Time since last update: **' + agelst[i] + '**'
                    i += 1
                if not idescription == '':
                    ititle = '**Top 5 prices for ' + content + '**'
                    em = discord.Embed(
                        title=ititle,
                        description=idescription,
                        color=0x00FF00
                    )

                    await message.channel.send(embed=em)
                    i += 1
            else:
                await message.channel.send('Unsupported or unknown mineral entered.')

        #Add user to DM list
        if message.content.startswith('!getalerts'):
            if not str(message.author.id) in self.dmset:
                self.alert_write(message.author)
                await message.channel.send('Added to alert list, DM incoming!')
                await message.author.send('You will now get a DM every time a a station is selling for at least 1.5m and demand is at least 2,000.  To unsubscribe, send the `!stopalerts` command in the channel you subscribed from.')
            else:
                await message.channel.send('You are already on the alert list.')

        #Delete user from DM list
        if message.content.startswith('!stopalerts'):
            self.alert_delete(message.author)
            await message.channel.send('You have been removed from the alert list.')
    
    async def on_ready(self):
        print('Checking for dm and membership files')
        self.file_create_check()
        print('Generating memberset')
        self.memberset_gen()
        print('Generating dmset')
        self.alertset_gen()
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

client = EDPriceCheckBot()
client.run(client.TOKEN)
