#importit
import discord
import xml.etree.ElementTree as ET
import requests
from discord.ext import commands, tasks
import datetime

jälkiruuat=["Korvapuusti","Pikkupulla","Omenavanukas"]

#ottaa tokenin config jsonista
def lueToken(tokentiedosto):
    with open(tokentiedosto, "r") as tiedosto:
        return tiedosto.read()
token = lueToken("token.txt")

#discord intentit
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

#bot client
client = discord.Client(intents=intents)

#asettaa url:n mistä ottaa ruokalistat
listaURL = "https://menu.kaarea.fi/KaareaAromieMenus/FI/Default/Kaarea/KERTTLU/Rss.aspx?Id=8ca4343a-1842-4584-88a7-172f560d14e4&DateMode=1"

#ottaa ruuat arkean sivulta ja ottaa turhat pätkät pois arkean sivun tiedostosta ja palauttaa kaikki ruuat ja pääruuat
viikonRuuat = {}
kaikkiRuoka = {}
def takeAway():
  file = requests.get(listaURL)
  root=ET.fromstring(file.content)
  for item in root[0].iter("item"):
    paiva = item[0].text.split(" ")[0]

    ruuat = item[1].text
  
    ruoka = ruuat.split("<")[0]
    kasvis = ruuat.split(">")[1]

    ruokaLyhyt = ruoka[ruoka.find(":") + 2:ruoka.find(")") + 1]
    kasvisLyhyt = kasvis[kasvis.find(":") + 2:kasvis.find(")") + 1]

    ruokaIso = ruoka[ruoka.find(":") + 2:len(ruoka)]
    kasvisIso = kasvis[kasvis.find(":") + 2:len(kasvis)]

    viikonRuuat[paiva] = [ruokaLyhyt, kasvisLyhyt] #viikon kaikki pääruuat ja niiden merkit (gluteeniton, laktoositon jne)
    kaikkiRuoka[paiva] = [ruokaIso, kasvisIso] #viikon kaikki ruuat, ei vaa pääruuat (tarvitaan pullacheckiin ja dmlistaan)
  return viikonRuuat,kaikkiRuoka
    #viikonRuuat["ma"][0] on Maanantai normiruoka
    #viikonRuuat["ti"][1] on Tiistai kasvisruoka
    #päivina ma-pe ja joka päivälle kasvis ja normi ruoka

@tasks.loop(time=datetime.time(hour=22))
async def uusiruokaTask():
    channel = client.get_channel(969179339675541515)
    await channel.send("moi")
    takeAway()

#login ja asettaa aktiviteetin (ja palauttaa ruuat)
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ruokalistoja"))
    takeAway()
    uusiruokaTask.start()

#jakaja, summa ja keskiarvo definattu
jakaja=0
summat=0
keskiarvo=0



#tekee ja lähettää embedin ja pingin (en osaa tehdä paremmin) kun käytetään !viikonlista
@client.event
async def on_message(message):
      #viikonlista komento
      if message.content.startswith('!viikonlista'):
        #ict 21 ping
        if message.channel.id==1066993762087219271:
          await message.channel.send("<@&977148653812736010>")
        #ict united ping
        elif message.channel.id==359247891958726656:
          await message.channel.send("<@&977149820886200381>")
        embed=discord.Embed(color=0x76b52f) #värin vaihto + embed defination
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/969179339675541515/1062375756568743956/Arkealogo.png") #arkealogo
        embed.add_field(name="Maanantain lounas:", value=kaikkiRuoka["ma"][0], inline=True) #maanantai
        embed.add_field(name="Maanantain kasvislounas:", value=kaikkiRuoka["ma"][1], inline=True)
        for jälkiruoka in jälkiruuat:
          if jälkiruoka in kaikkiRuoka["ma"][0]: #kattoo onko pullaa, jos on, rivin kolmas field ei ole tyhjä
            embed.add_field(name="Jälkiruokaa?!?!?", value="<:liikunnanitsenaiset:676730906802782228>", inline=True)
            tyhjäMA=False
            break
          else:
            tyhjäMA=True
        if tyhjäMA==True:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Tiistain lounas:", value=kaikkiRuoka["ti"][0], inline=True) #tiistai
        embed.add_field(name="Tiistain kasvislounas:", value=kaikkiRuoka["ti"][1], inline=True)
        for jälkiruoka in jälkiruuat:
          if jälkiruoka in kaikkiRuoka["ti"][0]:
            embed.add_field(name="ruokalassa on jälkiruokaa:", value="*visible happiness*", inline=True)
            tyhjäTI=False
            break
          else:
            tyhjäTI=True
        if tyhjäTI==True:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Keskiviikon lounas:", value=kaikkiRuoka["ke"][0], inline=True) #keskiviikko
        embed.add_field(name="Keskiviikon kasvislounas:", value=kaikkiRuoka["ke"][1], inline=True)
        for jälkiruoka in jälkiruuat:
          if jälkiruoka in kaikkiRuoka["ke"][0]:
            embed.add_field(name="jälkiruokaa tarjolla", value="<a:PoggersRow:519167666985107456>", inline=True)
            tyhjäKE=False
            break
          else:
            tyhjäKE=True
        if tyhjäKE==True:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Torstain lounas:", value=kaikkiRuoka["to"][0], inline=True) #torstai
        embed.add_field(name="Torstain kasvislounas:", value=kaikkiRuoka["to"][1], inline=True)
        for jälkiruoka in jälkiruuat:
          if jälkiruoka in kaikkiRuoka["to"][0]:
            embed.add_field(name="<:1605:677063766487203840>", value="owo uwu jee jälkiruokaa", inline=True)
            tyhjäTO=False
            break
          else:
            tyhjäTO=True
        if tyhjäTO==True:
          embed.add_field(name="", value="", inline=True)
        embed.add_field(name="Perjantain lounas:", value=kaikkiRuoka["pe"][0], inline=True) #perjantai
        embed.add_field(name="Perjantain kasvislounas:", value=kaikkiRuoka["pe"][1], inline=True)
        for jälkiruoka in jälkiruuat:
          if jälkiruoka in kaikkiRuoka["pe"][0]:
            embed.add_field(name="me when jälkiruoka", value="<:malsionilonen:921328363581341696>", inline=True)
            tyhjäPE=False
            break
          else:
            tyhjäPE=True
        if tyhjäPE==True:
          embed.add_field(name="", value="", inline=True)
        if message.channel.id==1066993762087219271:
          embed.set_footer(text=keskiarvo) #keskiarvo aluksi nolla
        msg=await message.channel.send("<:nomnom_onni:1020763115266248774>",embed=embed) #lähettää onnin + embedin samassa viestissä
        if message.channel.id==1066993762087219271:
          await msg.add_reaction("0️⃣")
          await msg.add_reaction("1️⃣") #lisätään reaktiot
          await msg.add_reaction("2️⃣")
          await msg.add_reaction("3️⃣")
          await msg.add_reaction("4️⃣")
          await msg.add_reaction("5️⃣")

#käyttäjä lisää reaktion
@client.event
async def on_reaction_add(reaction, user):
    global jakaja
    global summat
    global keskiarvo
    if reaction.emoji == "0️⃣" and not user.bot:
      jakaja+=1
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "1️⃣" and not user.bot:
      jakaja+=1
      summat+=1
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "2️⃣" and not user.bot:
      jakaja+=1
      summat+=2
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "3️⃣" and not user.bot:
      jakaja+=1
      summat+=3
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "4️⃣" and not user.bot:
      jakaja+=1
      summat+=4
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "5️⃣" and not user.bot:
      jakaja=+1
      summat+=5
      keskiarvo=(summat)/jakaja
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            pass
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)

#käyttäjä poistaa reaktion (if ja else sen takia että ei tule nollalla jakaminen)
@client.event
async def on_reaction_remove(reaction, user):
    global jakaja
    global summat
    global keskiarvo
    if reaction.emoji == "0️⃣" and not user.bot:
      jakaja-=1
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        pass
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "1️⃣" and not user.bot:
      jakaja-=1
      summat-=1
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        keskiarvo-=1
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "2️⃣" and not user.bot:
      jakaja-=1
      summat-=2
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        keskiarvo-=2
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "3️⃣" and not user.bot:
      jakaja-=1
      summat-=3
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        keskiarvo-=3
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "4️⃣" and not user.bot:
      jakaja-=1
      summat-=4
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        keskiarvo-=4
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)
    elif reaction.emoji == "5️⃣" and not user.bot:
      jakaja-=1
      summat-=5
      if jakaja!=0:
        keskiarvo=(summat)/jakaja
      else:
        keskiarvo-=5
      keskiarvo=round(keskiarvo, 2)
      embeds = reaction.message.embeds
      if embeds:
          embed = embeds[0]
      else:
            return
      embed.set_footer(text=keskiarvo)
      await reaction.message.edit(embed=embed)



#kirjautuu bottiin tokenilla (katso config.json)
client.run(token)