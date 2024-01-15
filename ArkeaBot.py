#importit
import discord
import xml.etree.ElementTree as ET
import requests
from discord.ext import tasks
import datetime
from random import randint

jälkiruuat=["Korvapuusti","Pikkupulla","Omenavanukas","Pannukakku","Vadelmamunkki","Marjakimara","Mehevä omenapiirakka"]

#discord intentit
intents = discord.Intents.default()
intents.message_content = True #näkee viestit
intents.members = True #näkee käyttäjät
intents.dm_messages = True #turha, dmiä varten

#bot client
client = discord.Client(intents=intents)

Guildlista={}
class ruokaGuild:
    def __init__(self, listaId, ruokala, arviointi,rooli) -> None:
      self.listaId=listaId
      self.ruokala=ruokala
      self.arviointi=arviointi
      self.rooli=rooli

def MitäSaisiOlla(uusiUrl):
  file = requests.get(uusiUrl,verify=False)
  filestr=(str(file.content))
  listid=filestr.find("Rss.aspx?Id=")
  iidee=filestr[listid+12:filestr.find("&",listid)]
  ruokala=uusiUrl[59:uusiUrl.find("/",59)]
  return iidee, ruokala

def lueguildlist(tiedosto):
   f=open(tiedosto,"r")
   for ruokalat in f.read().splitlines():
      j=ruokalat.split(" ")
      guildi=ruokaGuild(j[1],j[2],eval(j[3]),j[4])
      Guildlista[int(j[0])]=guildi

#ottaa ruuat arkean sivulta ja ottaa turhat pätkät pois arkean sivun tiedostosta ja palauttaa kaikki ruuat ja pääruuat
viikonRuuat = {}
kaikkiRuoka = {}
def takeAway(listaId,ruokala):
  listaURL="https://menu.kaarea.fi/KaareaAromieMenus/FI/Default/Kaarea/"+ruokala+"/Rss.aspx?Id="+listaId+"&DateMode=1"
  viikonRuuat.clear()
  kaikkiRuoka.clear()
  file = requests.get(listaURL,verify=False)
  root=ET.fromstring(file.content)
  for item in root[0].iter("item"):
    paiva = item[0].text.split(" ")[0]

    ruuat = item[1].text
  
    ruoka = ruuat.split("<br><")[0]
    kasvis = ruuat.split("<br><br>")[1]

    ruokaLyhyt = ruoka[ruoka.find(":")+2:ruoka.find(")") + 1]
    kasvisLyhyt = kasvis[kasvis.find(":")+2:kasvis.find(")") + 1]

    ruokaIso = ruoka[ruoka.find(":") + 1:len(ruoka)]
    kasvisIso = kasvis[kasvis.find(":") + 1:len(kasvis)]

    viikonRuuat[paiva] = [ruokaLyhyt, kasvisLyhyt] #viikon kaikki pääruuat ja niiden merkit (gluteeniton, laktoositon jne)
    kaikkiRuoka[paiva] = [ruokaIso, kasvisIso] #viikon kaikki ruuat, ei vaa pääruuat (tarvitaan pullacheckiin)
  return viikonRuuat,kaikkiRuoka
    #viikonRuuat["ma"][0] on Maanantai normiruoka
    #viikonRuuat["ti"][1] on Tiistai kasvisruoka
    #päivina ma-pe ja joka päivälle kasvis ja normi ruoka

timez=datetime.timezone(datetime.timedelta(hours=2))
time=datetime.time(hour=7,tzinfo=timez)

@tasks.loop(time=time)
async def uusiruokaTask():
    if datetime.date.today().weekday()==0:
      ruokaviestit.clear()
      for i in Guildlista:
        await viikonlistaviesti(i)

#login ja asettaa aktiviteetin (ja palauttaa ruuat)
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ruokalistoja"))
    lueguildlist("Guilds.txt")
    uusiruokaTask.start()

ruokaviestit = {}

#ruokaviesti class
class Viesti:
   def __init__(self) -> None:
      self.keskiarvo = 0 #keskiarvo, summa ja jakaja nollassa alussa
      self.summa = 0
      self.jakaja = 0

async def lisääkeskiarvo(viesti: Viesti,reaction,embed,uusiarvo):
  viesti.jakaja+=1 #reaktioiden määrä kasvaa
  viesti.summa+=uusiarvo #summaan lisätään uusi arvo
  viesti.keskiarvo=(viesti.summa)/viesti.jakaja #lasketaan keskiarvo
  viesti.keskiarvo=round(viesti.keskiarvo, 2) #pyöristys alas
  embed.set_footer(text=viesti.keskiarvo) #vaihdetaan footer
  await reaction.message.edit(embed=embed) #editataan viestiä

async def poistakeskiarvo(viesti: Viesti,reaction,embed,uusiarvo):
  viesti.jakaja-=1 #reaktioiden määrä laskee
  viesti.summa-=uusiarvo #poistetaan uusi arvo
  if viesti.jakaja!=0: #jos jakaja on nolla ei koiteta jakaa sillä
    viesti.keskiarvo=(viesti.summa)/viesti.jakaja
  else:
    viesti.keskiarvo-=uusiarvo
  viesti.keskiarvo=round(viesti.keskiarvo, 2)
  embed.set_footer(text=viesti.keskiarvo)
  await reaction.message.edit(embed=embed)

päivät={ #päivät + mitä se tarkoittaa
  1:["Maanantain","ma"],
  2:["Tiistain","ti"],
  3:["Keskiviikon","ke"],
  4:["Torstain","to"],
  5:["Perjantain","pe"],
}

async def viikonlistaviesti(lähetysid): #viikonlista funktiona jotta voi lähettää automaattisesti
        kanava=client.get_channel(lähetysid) #kanavaa tarvitaan viestin lähettämiseen
        try:
           guil=Guildlista[lähetysid]
        except:
           await kanava.send("Kanavaa ei ole rekisteröity!")
           return
        await kanava.send(guil.rooli)
        embed=discord.Embed(color=0x76b52f) #värin vaihto + embed defination
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/969179339675541515/1062375756568743956/Arkealogo.png") #arkealogo
        takeAway(guil.listaId,guil.ruokala)
        for i in range(1,6):
          embed.add_field(name=päivät[i][0]+" lounas:", value=kaikkiRuoka[päivät[i][1]][0], inline=True) #Lisää jokaisen päivän 2 ruokafieldiä
          embed.add_field(name=päivät[i][0]+" kasvislounas:", value=kaikkiRuoka[päivät[i][1]][1], inline=True)
          if any(jr in kaikkiRuoka[päivät[i][1]][0] for jr in jälkiruuat): #kattoo onko pullaa, jos on, rivin kolmas field ei ole tyhjä
            match randint(0,4): #random viesti jälkiruuasta
              case 0:
                  tieto="Jälkiruokaa?!?!?"
              case 1:
                  tieto="ruokalassa on jälkiruokaa:"
              case 2:
                  tieto="jälkiruokaa tarjolla"
              case 3:
                  tieto="owo uwu jee jälkiruokaa"
              case 4:
                  tieto="me when jälkiruoka"

            match randint(0,4): #random reaktio jälkiruuasta
              case 0:
                  reaktio="<:liikunnanitsenaiset:676730906802782228>"
              case 1:
                  reaktio="*visible happiness*"
              case 2:
                  reaktio="<a:PoggersRow:519167666985107456>"
              case 3:
                  reaktio="<:1605:677063766487203840>"
              case 4:
                  reaktio="<:malsionilonen:921328363581341696>"
            embed.add_field(name=tieto, value=reaktio, inline=True) #lisätään jälkiruokafield
          else:                      #jos jälkiruokaa ei ole, 
            embed.add_field(name="", value="", inline=True) #lisätään tyhjä field 

        if guil.arviointi==True: #jos lähetetään arvioitavalle
          embed.set_footer(text=0) #keskiarvo aluksi nolla
        elif datetime.date.today().isocalendar().week < 22: #jos on kesäkausi
          embed.set_footer(text=str(22-datetime.date.today().isocalendar().week) + " viikkoa kesälomaan")
        else: #jos on talvikausi
          embed.set_footer(text=str(datetime.date(datetime.date.today().year,12,22).isocalendar().week-datetime.date.today().isocalendar().week) + " viikkoa joululomaan")
        msg=await kanava.send("<:nomnom_onni:1020763115266248774>",embed=embed) #lähettää onnin + embedin samassa viestissä
        if guil.arviointi==True: #jos lähetetään ict21 servulle
          ruokaviesti = Viesti() #viestiobjekti
          ruokaviestit[msg.id] = ruokaviesti #lisätään objekti dictiin
          await msg.add_reaction("0️⃣")
          await msg.add_reaction("1️⃣") #lisätään reaktiot
          await msg.add_reaction("2️⃣")
          await msg.add_reaction("3️⃣")
          await msg.add_reaction("4️⃣")
          await msg.add_reaction("5️⃣")

#on message, kun saa viestin
@client.event
async def on_message(message):
      #viikonlista komento
      if message.content.startswith('!viikonlista'): 
        await viikonlistaviesti(message.channel.id) #lähettää viestin
      
      if message.content.startswith('!lisääruokala'):
          try: 
            Guildlista[message.channel.id]
          except:
             pass
          else:
            await message.channel.send("Ruokala on jo rekisteröity!")
            return
          splitmessage=message.content.split(" ")
          uusiID,uusiRuokala=MitäSaisiOlla(str(splitmessage[1]))
          uusiArviointi=eval(splitmessage[2])
          uusguild = ruokaGuild(uusiID,uusiRuokala,uusiArviointi,splitmessage[3])
          Guildlista[message.channel.id]=uusguild
          guildTiedosto=open("Guilds.txt","a")
          guildTiedosto.write(str(message.channel.id)+" "+uusiID+" "+uusiRuokala+" "+str(uusiArviointi)+" "+splitmessage[3]+"\n")
          guildTiedosto.close()
          await message.channel.send("Guild added"+uusiID+uusiRuokala)

#käyttäjä lisää reaktion
@client.event
async def on_reaction_add(reaction, user):
    embeds = reaction.message.embeds #ottaa viestin embedit
    if embeds: #jos embedejä on nii ottaa ekan
      embed = embeds[0]
    else:
      return #muuten cancelaa
    if reaction.message.id not in ruokaviestit: # tarkistaa onko viesti ruokaviesti olemassa
      return #jos ei oo olemassa cancelaa
    viesti: Viesti = ruokaviestit[reaction.message.id] #ottaa viestin mihin reagoitiin
    if reaction.emoji == "0️⃣" and not user.bot: #emojin + onko käyttäjä botti check
      await lisääkeskiarvo(viesti,reaction,embed,0)
    elif reaction.emoji == "1️⃣" and not user.bot:
      await lisääkeskiarvo(viesti,reaction,embed,1)
    elif reaction.emoji == "2️⃣" and not user.bot:
      await lisääkeskiarvo(viesti,reaction,embed,2)
    elif reaction.emoji == "3️⃣" and not user.bot:
      await lisääkeskiarvo(viesti,reaction,embed,3)
    elif reaction.emoji == "4️⃣" and not user.bot:
      await lisääkeskiarvo(viesti,reaction,embed,4)
    elif reaction.emoji == "5️⃣" and not user.bot:
      await lisääkeskiarvo(viesti,reaction,embed,5)


#käyttäjä poistaa reaktion
@client.event
async def on_reaction_remove(reaction, user):
    embeds = reaction.message.embeds #samat ku lisääkeskiarvo :D
    if embeds:
      embed = embeds[0]
    else:
      return
    if reaction.message.id not in ruokaviestit:  # tarkistaa onko viesti ruokaviesti olemassa
      return
    viesti: Viesti = ruokaviestit[reaction.message.id]
    if reaction.emoji == "0️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,0)
    elif reaction.emoji == "1️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,1)
    elif reaction.emoji == "2️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,2)
    elif reaction.emoji == "3️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,3)
    elif reaction.emoji == "4️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,4)
    elif reaction.emoji == "5️⃣" and not user.bot:
      await poistakeskiarvo(viesti,reaction,embed,5)

#kirjautuu bottiin tokenilla (katso token.txt)
client.run(open("token.txt","r").read())

