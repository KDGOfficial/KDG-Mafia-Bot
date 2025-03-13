import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Переменные для игры
players = {}  # {игрок: статус ("жив" или "мертв")}
roles = {}    # {игрок: роль}
game_running = False
votes = {}    # {игрок: количество голосов}
night_actions = {"mafia": None, "doctor": None, "detective": None}  # Действия ночи

ROLE_LIST = ["Мафия", "Мирный житель", "Доктор", "Детектив"]
MAFIA_COUNT = 1

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к игре!")

# Команда для начала игры
@bot.command()
async def start(ctx):
    global game_running, players, roles, votes
    if game_running:
        await ctx.send("Игра уже идет!")
        return
    
    game_running = True
    players.clear()
    roles.clear()
    votes.clear()
    await ctx.send("Игра в Мафию начинается! Присоединяйтесь командой `!join`.")

# Команда для присоединения
@bot.command()
async def join(ctx):
    if not game_running:
        await ctx.send("Игра еще не началась. Используйте `!start`, чтобы начать.")
        return
    if ctx.author in players:
        await ctx.send(f"{ctx.author.mention}, вы уже в игре!")
        return
    players[ctx.author] = "жив"
    await ctx.send(f"{ctx.author.mention} присоединился к игре! Текущих игроков: {len(players)}")

# Распределение ролей и начало ночи
@bot.command()
async def night(ctx):
    global roles, night_actions
    if not game_running:
        await ctx.send("Игра не началась!")
        return
    if len(players) < 4:
        await ctx.send("Нужно минимум 4 игрока для начала!")
        return
    
    # Распределяем роли
    player_list = list(players.keys())
    random.shuffle(player_list)
    
    mafia_count = max(1, len(players) // 4)
    role_dist = ([ "Мафия" ] * mafia_count + 
                 [ "Доктор" ] * 1 + 
                 [ "Детектив" ] * 1 + 
                 [ "Мирный житель" ] * (len(players) - mafia_count - 2))
    
    random.shuffle(role_dist)
    roles = {player: role_dist[i] for i, player in enumerate(player_list)}
    
    # Отправляем роли в личку
    for player, role in roles.items():
        try:
            await player.send(f"Ваша роль: **{role}**\nЕсли вы Мафия, Доктор или Детектив, используйте команды в ЛС бота: `!kill`, `!heal`, `!check`.")
        except:
            await ctx.send(f"Не удалось отправить роль {player.mention}")
    
    night_actions = {"mafia": None, "doctor": None, "detective": None}
    await ctx.send("Наступает ночь! Мафия, Доктор и Детектив, отправьте свои действия мне в ЛС. У вас 30 секунд.")
    
    # Таймер для ночи
    await asyncio.sleep(30)
    await process_night(ctx)

# Обработка ночных действий
async def process_night(ctx):
    global night_actions
    mafia_target = night_actions["mafia"]
    doctor_target = night_actions["doctor"]
    
    if mafia_target and mafia_target in players and players[mafia_target] == "жив":
        if mafia_target != doctor_target:  # Если доктор не спас
            players[mafia_target] = "мертв"
            await ctx.send(f"{mafia_target.mention} был убит ночью!")
        else:
            await ctx.send("Кто-то был атакован ночью, но спасен!")
    
    # Проверка детектива
    if night_actions["detective"] in roles:
        role = roles[night_actions["detective"]]
        await night_actions["detective"].send(f"Вы проверили {night_actions['detective'].mention}. Его роль: **{role}**")
    
    if not await check_game_state(ctx):
        await day_phase(ctx)

# Действия ночью (через ЛС)
@bot.event
async def on_message(message):
    if message.author == bot.user or not game_running or not message.channel.type == discord.ChannelType.private:
        await bot.process_commands(message)
        return
    
    if message.author not in players or players[message.author] != "жив":
        return
    
    role = roles.get(message.author)
    if role == "Мафия" and message.content.startswith("!kill"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "жив":
                night_actions["mafia"] = target
                await message.author.send(f"Вы выбрали убить {target.mention}.")
        except:
            await message.author.send("Укажите ID игрока, например: `!kill 123456789`")
    
    elif role == "Доктор" and message.content.startswith("!heal"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "жив":
                night_actions["doctor"] = target
                await message.author.send(f"Вы выбрали спасти {target.mention}.")
        except:
            await message.author.send("Укажите ID игрока, например: `!heal 123456789`")
    
    elif role == "Детектив" and message.content.startswith("!check"):
        try:
            target = await bot.fetch_user(int(message.content.split()[1]))
            if target in players and players[target] == "жив":
                night_actions["detective"] = target
                await message.author.send(f"Вы проверяете {target.mention}. Результат скоро придет.")
        except:
            await message.author.send("Укажите ID игрока, например: `!check 123456789`")
    
    await bot.process_commands(message)

# День и голосование
async def day_phase(ctx):
    global votes
    votes.clear()
    await ctx.send("Наступает день! Обсуждайте и голосуйте командой `!vote @игрок`. У вас 60 секунд.")
    
    # Даем время на голосование
    await asyncio.sleep(60)
    
    # Подсчет голосов
    if votes:
        eliminated = max(votes, key=votes.get)
        players[eliminated] = "мертв"
        await ctx.send(f"По итогам голосования был исключен {eliminated.mention}! Его роль была: **{roles[eliminated]}**")
    else:
        await ctx.send("Никто не проголосовал. День прошел без исключений.")
    
    # Проверка окончания игры
    if not await check_game_state(ctx):
        await ctx.send("Готовимся к следующей ночи...")
        await asyncio.sleep(5)
        await night(ctx)

@bot.command()
async def vote(ctx, member: discord.Member):
    if not game_running or ctx.author not in players or players[ctx.author] != "жив":
        await ctx.send("Вы не можете голосовать!")
        return
    if member not in players or players[member] != "жив":
        await ctx.send("Этот игрок не в игре или уже мертв!")
        return
    
    votes[member] = votes.get(member, 0) + 1
    await ctx.send(f"{ctx.author.mention} проголосовал за {member.mention}. Текущие голоса: {votes[member]}")

# Проверка состояния игры
async def check_game_state(ctx):
    global game_running
    alive_players = [p for p, s in players.items() if s == "жив"]
    mafia_alive = sum(1 for p in alive_players if roles[p] == "Мафия")
    non_mafia_alive = len(alive_players) - mafia_alive
    
    if mafia_alive == 0:
        await ctx.send("Мирные жители победили! Мафия уничтожена!")
        game_running = False
        return True
    elif mafia_alive >= non_mafia_alive:
        await ctx.send("Мафия победила! Они захватили город!")
        game_running = False
        return True
    return False

# Команда для завершения игры
@bot.command()
async def end(ctx):
    global game_running
    if not game_running:
        await ctx.send("Игра и так не идет!")
        return
    game_running = False
    players.clear()
    roles.clear()
    votes.clear()
    await ctx.send("Игра завершена!")

# Запуск бота
bot.run("YOUR_TOKEN_HERE")  # Замени на свой токен
