#importit
import discord
import schedule
import xml.etree.ElementTree as ET
import requests
import json

#ottaa tokenin configista
with open("./config.json") as config:
  configData = json.load(config)
token = configData["Token"]

vote=0

#discord intentit
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

client = discord.Client(intents=intents)

#etsii ruuan arkea sivulta
viikonRuuat = {}
kaikkiRuoka = {}
def takeAway():
  for item in root[0].iter("item"):
    paiva = item[0].text.split(" ")[0]

    ruuat = item[1].text
  
    ruoka = ruuat.split("<")[0]
    kasvis = ruuat.split(">")[1]

    ruokaLyhyt = ruoka[ruoka.find(":") + 2:ruoka.find(")") + 1]
    kasvisLyhyt = kasvis[kasvis.find(":") + 2:kasvis.find(")") + 1]

    ruoka = ruoka[ruoka.find(":") + 2:len(ruoka)]
    kasvis = kasvis[kasvis.find(":") + 2:len(kasvis)]

    viikonRuuat[paiva] = [ruokaLyhyt, kasvisLyhyt]
    kaikkiRuoka[paiva] = [ruoka, kasvis]
  return viikonRuuat,kaikkiRuoka
    #viikonRuuat["ma"][0] = Maanantai normi ruoka
    #viikonRuuat["ti"][1] = tiistai kasvis ruoka

#login ja asettaa aktiviteetin
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ruokalistoja"))
    takeAway()

#asettaa url:n mistä ottaa ruokalistat
listaURL = "https://menu.kaarea.fi/KaareaAromieMenus/FI/Default/Kaarea/KERTTLU/Rss.aspx?Id=8ca4343a-1842-4584-88a7-172f560d14e4&DateMode=1"
file = requests.get(listaURL)
root=ET.fromstring(file.content)

#tekee ja lähettää embedin (en osaa tehdä paremmin) kun käytetään !viikonlista
@client.event
async def on_message(message):
      if message.content.startswith('!viikonlista'):
        embed=discord.Embed(color=0x76b52f)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/969179339675541515/1062375756568743956/Arkealogo.png")
        embed.add_field(name="Maanantain lounas:", value=viikonRuuat["ma"][0], inline=True)
        embed.add_field(name="Maanantain kasvislounas:", value=viikonRuuat["ma"][1], inline=True)
        if "pulla" in kaikkiRuoka["ma"][0]:
          embed.add_field(name="Pullaa?!?!?", value="<:liikunnanitsenaiset:676730906802782228>", inline=True)
        else:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Tiistain lounas:", value=viikonRuuat["ti"][0], inline=True)
        embed.add_field(name="Tiistain kasvislounas:", value=viikonRuuat["ti"][1], inline=True)
        if "pulla" in kaikkiRuoka["ti"][0]:
          embed.add_field(name="ruokalassa on pullaa", value="*visible happiness*", inline=True)
        else:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Keskiviikon lounas:", value=viikonRuuat["ke"][0], inline=True)
        embed.add_field(name="Keskiviikon kasvislounas:", value=viikonRuuat["ke"][1], inline=True)
        if "pulla" in kaikkiRuoka["ke"][0]:
          embed.add_field(name="pullaa tarjolla", value="<a:PoggersRow:519167666985107456>", inline=True)
        else:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Torstain lounas:", value=viikonRuuat["to"][0], inline=True)
        embed.add_field(name="Torstain kasvislounas:", value=viikonRuuat["to"][1], inline=True)
        if "pulla" in kaikkiRuoka["to"][0]:
          embed.add_field(name="<:1605:677063766487203840>", value="owo uwu jee pullaa", inline=True)
        else:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Perjantain lounas:", value=viikonRuuat["pe"][0], inline=True)
        embed.add_field(name="Perjantain kasvislounas:", value=viikonRuuat["pe"][1], inline=True)
        if "pulla" in kaikkiRuoka["pe"][0]:
          embed.add_field(name="me when pulla", value="<:malsionilonen:921328363581341696>", inline=True)
        else:
          embed.add_field(name="", value="", inline=True)
        embed.set_footer(text=vote)
        await message.channel.send("<:nomnom_onni:1020763115266248774>",embed=embed)
        #ict 21
        if message.channel.id==957877822398017537:
          await message.channel.send("<@&977148653812736010>")
        #ict united
        elif message.channel.id==359247891958726656:
          await message.channel.send("<@&977149820886200381>")
        #await msg.add_reaction('1️⃣')
        #await msg.add_reaction('2️⃣')
        #await msg.add_reaction('3️⃣')
        #await msg.add_reaction('4️⃣')
        #await msg.add_reaction('5️⃣')

      #dmlista
      elif message.content.startswith('!dmlista'):
        dmembed=discord.Embed(color=0x76b52f)
        dmembed.set_thumbnail(url="https://media.discordapp.net/attachments/969179339675541515/1062375756568743956/Arkealogo.png")
        dmembed.add_field(name="Maanantain lounas", value=kaikkiRuoka["ma"][0], inline=True)
        dmembed.add_field(name="Maanantain kasvislounas", value=kaikkiRuoka["ma"][1], inline=True)
        dmembed.add_field(name="", value="", inline=True)
        dmembed.add_field(name="Tiistain lounas", value=kaikkiRuoka["ti"][0], inline=True)
        dmembed.add_field(name="Tiistain kasvislounas", value=kaikkiRuoka["ti"][1], inline=True)
        dmembed.add_field(name="", value="", inline=True)
        dmembed.add_field(name="Keskiviikon lounas", value=kaikkiRuoka["ke"][0], inline=True)
        dmembed.add_field(name="Keskiviikon kasvislounas", value=kaikkiRuoka["ke"][1], inline=True)
        dmembed.add_field(name="", value="", inline=True)
        dmembed.add_field(name="Torstain lounas", value=kaikkiRuoka["to"][0], inline=True)
        dmembed.add_field(name="Torstain kasvislounas", value=kaikkiRuoka["to"][1], inline=True)
        dmembed.add_field(name="", value="", inline=True)
        dmembed.add_field(name="Perjantain lounas", value=kaikkiRuoka["pe"][0], inline=True)
        dmembed.add_field(name="Perjantain kasvislounas", value=kaikkiRuoka["pe"][1], inline=True)
        dmembed.add_field(name="", value="", inline=True)
        await message.author.send("<:nomnom_onni:1020763115266248774>",embed=dmembed)

#kirjautuu bottiin tokenilla (katso config.json)
client.run(token)
