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

#discord intentit
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

#login ja asettaa aktiviteetin
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ruokalistoja"))

#asettaa url:n mistä ottaa ruokalistat
listaURL = "https://menu.kaarea.fi/KaareaAromieMenus/FI/Default/Kaarea/KERTTLU/Rss.aspx?Id=8ca4343a-1842-4584-88a7-172f560d14e4&DateMode=1"
file = requests.get(listaURL)
root=ET.fromstring(file.content)

#etsii ruuan arkea sivulta
viikonRuuat = {}
kaikkiRuoka = {}

for item in root[0].iter("item"):
  paiva = item[0].text.split(" ")[0]

  ruuat = item[1].text
  
  ruoka = ruuat.split("<")[0]
  kasvis = ruuat.split(">")[1]

  ruokaLyhyt = ruoka[ruoka.find(":") + 2:ruoka.find(")") + 1]
  kasvisLyhyt = kasvis[kasvis.find(":") + 2:kasvis.find(")") + 1]

  viikonRuuat[paiva] = [ruokaLyhyt, kasvisLyhyt]
  kaikkiRuoka[paiva] = [ruoka, kasvis]
  #viikonRuuat["ma"][0] = Maanantai normi ruoka
  #viikonRuuat["ti"][1] = tiistai kasvis ruoka

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
        #embed.set_footer(text="Viikon ruoka on x/5")
        await message.channel.send("<:nomnom_onni:1020763115266248774>",embed=embed)
        
#kirjautuu bottiin tokenilla (katso config.json)
client.run(token)
