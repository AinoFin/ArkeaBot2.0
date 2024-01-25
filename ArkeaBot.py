import discord #discord.py
import xml.etree.ElementTree as ET #ruokalistan pilkkomiseen
import requests #ruokalistan lataamiseen
from discord.ext import tasks #ruokataskin loopiin
import datetime #ajan lomaan mittaamiseen
from random import randint #randomisoituun reaktioon jälkiruokaan :D

jälkiruuat=["Korvapuusti","Pikkupulla","Omenavanukas","Pannukakku","Vadelmamunkki","Marjakimara","Mehevä omenapiirakka"]

#discord intentit
intents = discord.Intents.default()
intents.message_content = True #näkee viestit
intents.members = True #näkee käyttäjät
intents.dm_messages = True #turha, dmiä varten

#bot client
client = discord.Client(intents=intents)

#lista Guildeista (palvelimista) jolle laitetaan listoja
Guildlista={}
class ruokaGuild:
    def __init__(self, listaId, ruokala, arviointi,rooli) -> None:
      self.listaId=listaId
      self.ruokala=ruokala
      self.arviointi=arviointi
      self.rooli=rooli

def MitäSaisiOlla(uusiUrl): #urlstä kaarea id ja ruokalanimi etsijä
  file = requests.get(uusiUrl,verify=False) #false koska kaarean sivu on paska
  filestr=(str(file.content)) 
  listid=filestr.find("Rss.aspx?Id=") #etitään id
  iidee=filestr[listid+12:filestr.find("&",listid)] #otetaan id
  ruokala=uusiUrl[59:uusiUrl.find("/",59)] #otetaan ruokalan nimi
  return iidee, ruokala

def lueguildlist(tiedosto): #luetaan Guilds.txt alussa jotta saadaan rekisteröidyt ruokalat takaisin
   f=open(tiedosto,"r")
   for ruokalat in f.read().splitlines(): #yksi ruokala per rivi
      j=ruokalat.split(" ")
      guildi=ruokaGuild(j[1],j[2],eval(j[3]),j[4]) #1=kaareaid, 2=kaarea ruokala, 3=arviointi, 4=pingattava rooli
      Guildlista[int(j[0])]=guildi #0=discord kanavan id

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

    viikonRuuat[paiva] = [ruokaLyhyt, kasvisLyhyt] #viikon kaikki pääruuat ja niiden merkit (tällä hetkellä ei käytössä)
    kaikkiRuoka[paiva] = [ruokaIso, kasvisIso] #viikon kaikki ruuat, ei vaa pääruuat

    if "Uunimakkara" in kaikkiRuoka[paiva][0]: #UUNIMAKKARACHECK, TÄRKEIN OSA KOODIA
      kaikkiRuoka[paiva][0]=kaikkiRuoka[paiva][0].replace("Uunimakkara","UUUNIMAKKAARAAAAOUUUUYHJEAAAAHBOYYYYYYY")
  return viikonRuuat,kaikkiRuoka
    #kaikkiRuoka["ma"][0] on Maanantai normiruoka
    #kaikkiRuoka["ti"][1] on Tiistai kasvisruoka
    #päivina ma-pe ja joka päivälle kasvis ja normi ruoka

timez=datetime.timezone(datetime.timedelta(hours=2)) #suomi on +2 aikavyöhykkeellä
time=datetime.time(hour=7,tzinfo=timez) #aamuseiskalta ruokalistat

@tasks.loop(time=time) #ruokataskloop
async def uusiruokaTask():
    if datetime.date.today().weekday()==0: #jos on maanantai
      ruokaviestit.clear() #vanhat viestit pois
      for i in Guildlista: #jokaseen guildiin viesti
        await viikonlistaviesti(i)

#login ja asettaa aktiviteetin (ja palauttaa ruuat)
@client.event
async def on_ready():
    print(f'Logged in as {client.user}') #ei periaatteessa tarvis mutta on mukava olla :)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ruokalistoja")) #suomeksi kääntyy "katsotaan ruokalistoja"
    lueguildlist("Guilds.txt") #luetaan guildit
    uusiruokaTask.start() #aloitetaan viikottaisten viestien lähettäminen

#ruokaviesti dict ja class
ruokaviestit = {}
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
           guil=Guildlista[lähetysid] #jos kanavaa ei ole jo
        except:
           await kanava.send("Kanavaa ei ole rekisteröity!")
           return
        await kanava.send(guil.rooli) #lähetetään ping erikseen jotta onni on iso emoji
        embed=discord.Embed(color=0x76b52f) #värin vaihto + embed defination
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/969179339675541515/1062375756568743956/Arkealogo.png") #arkealogo
        takeAway(guil.listaId,guil.ruokala)
        for i in range(1,6):
          embed.add_field(name=päivät[i][0]+" lounas:", value=kaikkiRuoka[päivät[i][1]][0], inline=True) #Lisää jokaisen päivän 2 ruokafieldiä
          embed.add_field(name=päivät[i][0]+" kasvislounas:", value=kaikkiRuoka[päivät[i][1]][1], inline=True)
          if any(jr in kaikkiRuoka[päivät[i][1]][0] for jr in jälkiruuat): #kattoo onko jälkiruokaa, jos on, rivin kolmas field ei ole tyhjä
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
          else:
            embed.add_field(name="", value="", inline=True) #lisätään tyhjä field jos jälkiruokaa ei ole 

        if guil.arviointi==True: #jos lähetetään arvioitavalle
          embed.set_footer(text=0) #keskiarvo aluksi nolla
        elif datetime.date.today().isocalendar().week < 22: #jos on kesäkausi
          embed.set_footer(text=str(22-datetime.date.today().isocalendar().week) + " viikkoa kesälomaan")
        else: #jos on talvikausi
          embed.set_footer(text=str(datetime.date(datetime.date.today().year,12,22).isocalendar().week-datetime.date.today().isocalendar().week) + " viikkoa joululomaan")
        msg=await kanava.send("<:nomnom_onni:1020763115266248774>",embed=embed) #lähettää onnin + embedin samassa viestissä
        if guil.arviointi==True: #jos lähetetään arvioitavalle servulle
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
      if message.content.startswith('!viikonlista'): #viikonlista komento
        await viikonlistaviesti(message.channel.id) #lähettää viestin
      
      if message.content.startswith('!lisääruokala'):
          try: 
            Guildlista[message.channel.id] #jos guildia ei ole tulee virhe (täs kohtaa halutaan virhe)
          except:
             pass #jatketaan koodin suorittamista
          else:
            await message.channel.send("Ruokala on jo rekisteröity!") #jos ei anna vihettä nii guild on jo, joten ei lisätä sitä
            return
          splitmessage=message.content.split(" ") #jaetaan viesti
          uusiID,uusiRuokala=MitäSaisiOlla(str(splitmessage[1]))
          uusiArviointi=eval(splitmessage[2])
          uusguild = ruokaGuild(uusiID,uusiRuokala,uusiArviointi,splitmessage[3]) #tehdään uusi ruokaGuild objekti
          Guildlista[message.channel.id]=uusguild #lisätään ruokaGuild listaan
          guildTiedosto=open("Guilds.txt","a") #kirjoitetaan ruokaGuild tiedostoon (a, jotta päästään tiedoston loppuun)
          guildTiedosto.write(str(message.channel.id)+" "+uusiID+" "+uusiRuokala+" "+str(uusiArviointi)+" "+splitmessage[3]+"\n")
          guildTiedosto.close()
          await message.channel.send("Ruokala lisätty!")

#käyttäjä lisää reaktion
@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.id not in ruokaviestit: # tarkistaa onko viesti ruokaviesti olemassa
      return #jos ei oo olemassa cancelaa
    embeds = reaction.message.embeds #ottaa viestin embedit
    embed = embeds[0]
    viesti: Viesti = ruokaviestit[reaction.message.id] #ottaa viestin mihin reagoitiin
    if not user.bot:
      match reaction.emoji:
        case "0️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,0)
        case "1️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,1)
        case "2️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,2)
        case "3️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,3)
        case "4️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,4)
        case "5️⃣":
            await lisääkeskiarvo(viesti,reaction,embed,5)

#käyttäjä poistaa reaktion
@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.id not in ruokaviestit:  # tarkistaa onko viesti ruokaviesti olemassa
      return
    embeds = reaction.message.embeds #samat ku lisääkeskiarvo :D
    embed = embeds[0]
    viesti: Viesti = ruokaviestit[reaction.message.id]
    if not user.bot:
      match reaction.emoji:
        case "0️⃣":
            await poistakeskiarvo(viesti,reaction,embed,0)
        case "1️⃣":
            await poistakeskiarvo(viesti,reaction,embed,1)
        case "2️⃣":
            await poistakeskiarvo(viesti,reaction,embed,2)
        case "3️⃣":
            await poistakeskiarvo(viesti,reaction,embed,3)
        case "4️⃣":
            await poistakeskiarvo(viesti,reaction,embed,4)
        case "5️⃣":
            await poistakeskiarvo(viesti,reaction,embed,5)

#kirjautuu bottiin tokenilla (katso token.txt)
client.run(open("token.txt","r").read())

