"""
Welcome to Autumna1Equin0x's free to use Ban bot! This bot was coded by Autumna1Equin0x (Autumn). I made the bot to ban spy.pet
accounts, and used it in my own servers. I give you full permission to modify my code as you see fit, just as long as you give
me credit for the parts I made.

To use this script, add a custom bot to the server you want, and make sure it has ban perms. Paste the token into the token variable.
Once the bot is added and the token is pasted, type ">run" in the server you want to ban the accounts in. The bot will automatically
ban any members in the list of accounts.

NOTE: I made this at like 2 am so there's gonna be spelling errors
"""

'''
Import statements are crucial statments that allow the bot to run code you didn't create yourself
- The discord module includes all the code that allows the bot to connect to the Discord API
- The sys module allows you to run system commands
- The time module allows you to time how long some task takes
'''
import discord
import sys
import time
import os
from main import eclipse_id

# This is the bot prefix. This tells the bot what to look for at the start of a message.
prefix = '>'

# This is the bot Token. It's like the bots password. DO NOT SHARE THE TOKEN WITH ANYONE.
token = ''  # paste token between the quotes

# list of accounts to ban
# last updated 2024-04-22 06:43 UTC with spy.pet accounts
accounts = [
        "928350122843193385",
        "1185047194261274665",
        "956202276408688650",
        "956104664821157918",
        "1185047092478095443",
        "1185046791826178099",
        "1185047045413797898",
        "928483283698851901",
        "1185047444619284641",
        "1172086562176114689",
        "956294250927120436",
        "1185045560273666170",
        "1185046383015760016",
        "1210165420493905982",
        "978778806863151114",
        "1185030898148724777",
        "976786710836944936",
        "1185047847557672993",
        "1185036634270478406",
        "1185042820009054312",
        "1185035242222923927",
        "956075132571508757",
        "956164930061619230",
        "956131426250657862",
        "974926574346440765",
        "956192794014269481",
        "1185044083996098590",
        "1185047344023081011",
        "1185045337325449267",
        "1185043681737179197",
        "1172080432389574690",
        "956222023816847411",
        "956323664062722100",
        "928561259069177947",
        "956173030218940486",
        "1185045242706153573",
        "1185043970150117467",
        "1185033074304630936",
        "928355373763674162",
        "956037057157943377",
        "956375867632799787",
        "1185048077468450947",
        "1185038000795680769",
        "928369956716937287",
        "932098848900411423",
        "928318741060673627",
        "1185037104523268189",
        "932086630767013908",
        "956237066503585873",
        "1185021551825920066",
        "1185019322331045902",
        "919301068620435467",
        "932079867003039804",
        "1185036106257944677",
        "932033861699919882",
        "1185047968886308895",
        "1185045519576338442",
        "1185034806908682281",
        "956035417860362308",
        "956131521733984287",
        "1171219789738410037",
        "932096380879667253",
        "1185039045747818610",
        "1172076548791226439",
        "956128945227567145",
        "1185047411605897301",
        "1185033314189443133",
        "1185035279791292469",
        "1185051129147555890",
        "923404990511480852",
        "928591647611179018",
        "1185046309976166460",
        "1185045871478448242",
        "928586086828085358",
        "956153059371810836",
        "1185046537944973383",
        "956350881241104495",
        "956178931512410222",
        "1171205707576660133",
        "959468187328589845",
        "928490228841328680",
        "932082311263039488",
        "956054319529066527",
        "1171196139647803513",
        "956210819325132921",
        "1185038257789079614",
        "928453229740712006",
        "956246550152118374",
        "928600396002373633",
        "956261113115336774",
        "1172105789494792242",
        "1185050948675047539",
        "1210170987073503265",
        "956069338820001837",
        "956137602564640799",
        "1185046163473309696",
        "923435722025869312",
        "1185039549991235654",
        "1171197414632341508",
        "1171223723714556015",
        "923422685541851196",
        "1171223836973338634",
        "956097947727179806",
        "1210161585658798100",
        "932041199282454528",
        "932084358326681662",
        "956119888991232050",
        "932067526681186414",
        "1185047033183227947",
        "932057102841708655",
        "1185047344148918509",
        "956080137932259398",
        "1185039817231323187",
        "975468900244398151",
        "1172073543836631040",
        "928398544392560743",
        "956126507984637982",
        "956092289552384010",
        "1171227973450469426",
        "956172424309784617",
        "1185043981785112728",
        "1185033301099020311",
        "1185045436331982848",
        "932054618568032336",
        "1171191966059466802",
        "1171206094794797191",
        "1185037967992037489",
        "1172074070901264404",
        "1171225487494893622",
        "1185010648120303717",
        "932070704042631219",
        "923426902574759976",
        "1185045420594974761",
        "1185036303155335240",
        "1185038424101629962",
        "932094826059563040",
        "1185044808637616159",
        "956292731880239176",
        "1185038081322135603",
        "1171204995392209047",
        "1185039095211241552",
        "956031608144666665",
        "1185043232661450814",
        "956200330251624468",
        "932033514931650640",
        "1210174835985088532",
        "1210212474780127232",
        "956887823024275487",
        "928366751090106368",
        "1185034487537606676",
        "1185044716111265799",
        "1210158972280111164",
        "956004017299927061",
        "932039160854872084",
        "928549000431407164",
        "956157904539512874",
        "1230906926901104662",
        "1136350500296593571",
        "1138182474111922276",
        "1149015679010341005",
        "1133065473848770641",
        "1158776460320964628",
        "1194401785780117658",
        "1193574076854321202",
        "1193374643814404147",
        "1193680105524957324",
        "1193683318466695209",
        "1193679737734836286",
        "1193499415474884658",
        "1193458642217877604",
        "1193507529846693909",
        "1193509926471995473",
        "1193687334139461683",
        "1193521589992562813",
        "1193562785842475071",
        "1193520826159464453",
        "1193515568351936542",
        "1193542494424674305",
        "1193557060399407134",
        "1193508835403501619",
        "1193494110804381759",
        "1193502454537519134",
        "1193530565392093245",
        "1193254983576064191",
        "1193499142652166178",
        "1193514462435610665",
        "1193516940363309220",
        "1193541874745622660",
        "1193515539998457938",
        "1193478652541816896",
        "1193565065778040895",
        "1193542369019166804",
        "1193581763797205083",
        "1193530848268537978",
        "1193358225576304772",
        "1193494352660529192",
        "1193504268162973707",
        "1193543904671322144",
        "1193548530481115218",
        "1193552475068833883",
        "1193552905261817968",
        "1193560727252914186",
        "1193561382059262014",
        "1193566464746192917",
        "1193571027683377204",
        "1193540116342390816",
        "1193582027132370974",
        "1193574512797691974",
        "1193566714026270863",
        "1193682823366856794",
        "1193674324268285954",
        "1193690281032286379",
        "1193688338541072425",
        "1193684195227222036",
        "1193696131960553585",
        "1193689185043886163",
        "1192977716560007312",
        "1193690508669759518",
        "1193686734261735555",
        "1193687950320488489",
        "1193685126928924724",
        "1193688366953267212",
        "1193692159770120214",
        "1193680409662345297",
        "1193696237598281750",
        "1193521818972192858",
        "1193574667735277640",
        "1193582919957102753",
        "1193520613382430720",
        "932082257689190450",
        "923351918439436309",
        "1232366335468769376",
        "1193691695263531108",
        "1193690489736663134",
        "1193689410751967333",
        "1193685321087471749",
        "1193684934552981616",
        "1193692634548555778",
        "1193687145261576292",
        "1193686021943070893",
        "1193691805317873795",
        "1193690167786082307",
        "965813244549808159",
        "1193683078967738381",
        "1193697560955723846",
        "1193696921227886682",
        "1193687516264529970",
        "1193644793029480478",
        "1193681998531797193",
        "1193682515492343908",
        "964468503178522624",
        "1193689438790897765",
        "1193694086658531469",
        "973506429497516052",
        "964973543777529888",
        "973246753421803601",
        "1193672181314502706",
        "964068890084798475",
        "965928071830061086",
        "965860150860738590",
        "964001968207061002",
        "964702615982202990",
        "965822631985184819",
        "964082956845064222",
        "1193654608833282141",
        "1193684949128200275"
        ]

# This sets the bot's Activity status. It allows the bot to go into more detail about its current
# status
game = discord.Game('Send ">run" to ban spy.pet accounts')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# The client is the bot's discord account. It allows the bot to connect to discord and run commands
client = discord.Client(intents=intents)


class PsuedoMember:
    """
    Fake member class for compatibility with discords API
    """
    
    def __init__(self, accID):
        self.id = int(accID)


async def run(message):
    """
    Bans all accounts listed in the list of accounts to ban
    """
    i = 0
    print('├ GETTING MEMBER LIST')
    print('├ PURGING SERVER')
    print('├┐')
    for target in accounts:
        try:
            await message.guild.ban(PsuedoMember(target),
                                    reason='spy.pet account https://gist.github.com/Dziurwa14/05db50c66e4dcc67d129838e1b9d739a',
                                    delete_message_seconds=0)
            print(f'│├ <@{target}> BANNED')
            await message.guild.fet
            i += 1
        except Exception as e:
            print(f'│├ {repr(e)}')
    await message.channel.send(f'{i} account(s) banned')
    sys.exit()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


switcher = {'run': run}


@client.event
async def on_message(message):
    """
    When a message happens, it scans the first character for the bot prefix. If the first character
    is the bot prefix, the bot will attempt to run the command. If the command is in the switcher,
    the command will run and the bot should return an output, and respond in the same channel.
    Last docstring edit: -Autumn V1.0.0
    Last method edit: -Autumn V1.0.0
    :param message: the message that was just sent
    :return: None
    """
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)  # allows for fast transfer of data from discord to your command
            # line


'''This is what begins the entire bot, and tells the bot to run
THIS LINE MUST BE AT THE END OF THE SCRIPT.
IF THIS LINE IS NOT LAST, ANYTHING AFTER IT WILL NOT LOAD.'''
try:
    client.run(token)
except discord.errors.LoginFailure:
    print('Incorrect credentials. Did you set the bots token properly?')
