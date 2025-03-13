import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ���������� ��� ����
players = {}  # {�����: ������ ("���" ��� "�����")}
roles = {}    # {�����: ����}
game_running = False
votes = {}    # {�����: ���������� �������}
night_actions = {"mafia": None, "doctor": None, "detective": None}  # �������� ����

ROLE_LIST = ["�����", "������ ������", "������", "��������"]
MAFIA_COUNT = 1

@bot.event
async def on_ready():
    print(f"��� {bot.user} ����� � ����!")

# ������� ��� ������ ����
@bot.command()
async def start(ctx):
    global game_running, players, roles, votes
    if game_running:
        await ctx.send("���� ��� ����!")
        return
    
    game_running = True
    players.clear()
    roles.clear()
    votes.clear()
    await ctx.send("���� � ����� ����������! ��������������� �������� `!join`.")

# ������� ��� �������������
@bot.command()
async def join(ctx):
    if not game_running:
        await ctx.send("���� ��� �� ��������. ����������� `!start`, ����� ������.")
        return
    if ctx.author in players:
        await ctx.send(f"{ctx.author.mention}, �� ��� � ����!")
        return
    players[ctx.author] = "���"
    await ctx.send(f"{ctx.author.mention} ������������� � ����! ������� �������: {len(players)}")

# ������������� ����� � ������ ����
@bot.command()
async def night(ctx):
    global roles, night_actions
    if not game_running:
        await ctx.send("���� �� ��������!")
        return
    if len(players) < 4:
        await ctx.send("����� ������� 4 ������ ��� ������!")
        return
    
    # ������������ ����
    player_list = list(players.keys())
    random.shuffle(player_list)
    
    mafia_count = max(1, len(players) // 4)
    role_dist = ([ "�����" ] * mafia_count + 
                 [ "������" ] * 1 + 
                 [ "��������" ] * 1 + 
                 [ "������ ������" ] * (len(players) - mafia_count - 2))
    
    random.shuffle(role_dist)
    roles = {player: role_dist[i] for i, player in enumerate(player_list)}
    
    # ���������� ���� � �����
    for player, role in roles.items():
        try:
            await player.send(f"���� ����: **{role}**\n���� �� �����, ������ ��� ��������, ����������� ������� � �� ����: `!kill`, `!heal`, `!check`.")
        except:
            await ctx.send(f"�� ������� ��������� ���� {player.mention}")
    
    night_actions = {"mafia": None, "doctor": None, "detective": None}
    await ctx.send("��������� ����! �����, ������ � ��������, ��������� ���� �������� ��� � ��. � ��� 30 ������.")
    
    # ������ ��� ����
    await asyncio.sleep(30)
    await process_night(ctx)

# ��������� ������ ��������
async def process_night(ctx):
    global night_actions
    mafia_target = night_actions["mafia"]
    doctor_target = night_actions["doctor"]
    
    if mafia_target and mafia_target in players and players[mafia_target] == "���":
        if mafia_target != doctor_target:  # ���� ������ �� ����
            players[mafia_target] = "�����"
            await ctx.send(f"{mafia_target.mention} ��� ���� �����!")
        else:
            await ctx.send("���-�� ��� �������� �����, �� ������!")
    
    # �������� ���������
    if night_actions["detective"] in roles:
        role = roles[night_actions["detective"]]
        await night_actions["detective"].send(f"�� ��������� {night_actions['detective'].mention}. ��� ����: **{role}**")
    
    if not await check_game_state(ctx):
        await day_phase(ctx)

# �������� ����� (����� ��)
@bot.event
async def on_message(message):
    if message.author == bot.user or not game_running or not message.channel.type == discord.ChannelType.private:
        await bot.process_commands(message)
        return
    
    if message.author not in players or players[message.author] != "���":
        return
    
    role = roles.get(message.author)
    if role == "�����" and message.content.startswith("!kill"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "���":
                night_actions["mafia"] = target
                await message.author.send(f"�� ������� ����� {target.mention}.")
        except:
            await message.author.send("������� ID ������, ��������: `!kill 123456789`")
    
    elif role == "������" and message.content.startswith("!heal"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "���":
                night_actions["doctor"] = target
                await message.author.send(f"�� ������� ������ {target.mention}.")
        except:
            await message.author.send("������� ID ������, ��������: `!heal 123456789`")
    
    elif role == "��������" and message.content.startswith("!check"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "���":
                night_actions["detective"] = target
                await message.author.send(f"�� ���������� {target.mention}. ��������� ����� ������.")
        except:
            await message.author.send("������� ID ������, ��������: `!check 123456789`")
    
    await bot.process_commands(message)

# ���� � �����������
async def day_phase(ctx):
    global votes
    votes.clear()
    await ctx.send("��������� ����! ���������� � ��������� �������� `!vote @�����`. � ��� 60 ������.")
    
    # ���� ����� �� �����������
    await asyncio.sleep(60)
    
    # ������� �������
    if votes:
        eliminated = max(votes, key=votes.get)
        players[eliminated] = "�����"
        await ctx.send(f"�� ������ ����������� ��� �������� {eliminated.mention}! ��� ���� ����: **{roles[eliminated]}**")
    else:
        await ctx.send("����� �� ������������. ���� ������ ��� ����������.")
    
    # �������� ��������� ����
    if not await check_game_state(ctx):
        await ctx.send("��������� � ��������� ����...")
        await asyncio.sleep(5)
        await night(ctx)

@bot.command()
async def vote(ctx, member: discord.Member):
    if not game_running or ctx.author not in players or players[ctx.author] != "���":
        await ctx.send("�� �� ������ ����������!")
        return
    if member not in players or players[member] != "���":
        await ctx.send("���� ����� �� � ���� ��� ��� �����!")
        return
    
    votes[member] = votes.get(member, 0) + 1
    await ctx.send(f"{ctx.author.mention} ������������ �� {member.mention}. ������� ������: {votes[member]}")

# �������� ��������� ����
async def check_game_state(ctx):
    global game_running
    alive_players = [p for p, s in players.items() if s == "���"]
    mafia_alive = sum(1 for p in alive_players if roles[p] == "�����")
    non_mafia_alive = len(alive_players) - mafia_alive
    
    if mafia_alive == 0:
        await ctx.send("������ ������ ��������! ����� ����������!")
        game_running = False
        return True
    elif mafia_alive >= non_mafia_alive:
        await ctx.send("����� ��������! ��� ��������� �����!")
        game_running = False
        return True
    return False

# ������� ��� ���������� ����
@bot.command()
async def end(ctx):
    global game_running
    if not game_running:
        await ctx.send("���� � ��� �� ����!")
        return
    game_running = False
    players.clear()
    roles.clear()
    votes.clear()
    await ctx.send("���� ���������!")

# ������ ����
bot.run("YOUR_TOKEN_HERE")  # ������ �� ���� �����
