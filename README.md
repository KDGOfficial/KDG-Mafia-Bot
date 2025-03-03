Добавлю лицензию в конец поста. Я выберу MIT License, так как она простая, популярная и позволяет свободно использовать, изменять и распространять код при указании авторства. Если нужна другая (например, GPL или Apache), дай знать!

Вот окончательный вариант с лицензией:

---

# KDG-Mafia-Bot

**"KDG-Mafia-Bot — это Discord-бот для игры в 'Мафию'. Организуй увлекательные партии с друзьями: распределяй роли, управляй ночными действиями (Мафия, Доктор, Детектив) через ЛС, проводи голосования и следи за ходом игры с автоматической сменой дня и ночи. Написан на Python с использованием discord.py. Готов к запуску и кастомизации!"**

## Особенности KDG-Mafia-Bot

1. **Динамическое распределение ролей**  
   - Автоматически распределяет роли (Мафия, Мирный житель, Доктор, Детектив) в зависимости от числа игроков.  
   - Количество мафии рассчитывается как 1 на каждые 4 игрока (минимум 1), что обеспечивает баланс.

2. **Ночная фаза через ЛС**  
   - Мафия использует команду `!kill <ID>` для выбора жертвы.  
   - Доктор использует `!heal <ID>` для спасения игрока.  
   - Детектив использует `!check <ID>` для проверки роли другого игрока.  
   - Все действия отправляются боту в личные сообщения, сохраняя конфиденциальность.

3. **Автоматическая смена фаз**  
   - Ночь длится 30 секунд, день — 60 секунд (настраиваемые таймеры с помощью `asyncio.sleep`).  
   - После ночи автоматически обрабатываются действия и начинается день, затем цикл повторяется.

4. **Голосование и исключение**  
   - Игроки голосуют командой `!vote @игрок` в общем канале.  
   - После окончания дневной фазы подсчитываются голоса, и игрок с большинством исключается из игры.

5. **Отслеживание состояния игры**  
   - Ведется учет живых и мертвых игроков.  
   - Проверяются условия победы:  
     - Мирные побеждают, если все мафии мертвы.  
     - Мафия побеждает, если их число сравнялось или превысило число живых мирных жителей.

6. **Простота управления**  
   - Команды: `!start` (начать игру), `!join` (присоединиться), `!night` (начать ночь), `!vote @игрок` (голосовать), `!end` (завершить игру).  
   - Интуитивный запуск и минимальная настройка — достаточно вставить токен Discord-бота.

7. **Гибкость и расширяемость**  
   - Код написан на Python с использованием библиотеки `discord.py`, что упрощает модификацию.  
   - Легко добавить новые роли, изменить длительность фаз или улучшить интерфейс (например, с помощью эмбедов).

8. **Устойчивость к ошибкам**  
   - Проверки на наличие игры, участие игрока, статус "жив/мертв" предотвращают некорректные действия.  
   - Обработка исключений при отправке ЛС или выборе цели.

## Инструкция по установке

1. **Предварительные требования**  
   - Установите Python 3.8 или выше.  
   - Убедитесь, что у вас есть доступ к командной строке (терминал).

2. **Установка зависимостей**  
   - Установите библиотеку `discord.py` с помощью команды:  
     ```bash
     pip install discord.py
     ```

3. **Создание Discord-бота**  
   - Перейдите на [Discord Developer Portal](https://discord.com/developers/applications).  
   - Создайте новое приложение, добавьте бота и скопируйте его **токен**.  
   - Включите "Privileged Gateway Intents" (Message Content Intent и Server Members Intent) в разделе "Bot".

4. **Настройка бота**  
   - Скачайте или скопируйте код из репозитория.  
   - Откройте файл с кодом и замените `"YOUR_TOKEN_HERE"` на токен вашего бота:  
     ```python
     bot.run("ВАШ_ТОКЕН")
     ```

5. **Добавление бота на сервер**  
   - Сгенерируйте ссылку для приглашения бота в разделе "OAuth2 -> URL Generator":  
     - Выберите scopes: `bot`.  
     - Выберите permissions: `Send Messages`, `Read Messages/View Channels`.  
   - Скопируйте ссылку и добавьте бота на свой Discord-сервер.

6. **Запуск бота**  
   - В терминале перейдите в папку с файлом бота и выполните:  
     ```bash
     python имя_файла.py
     ```
   - Если все настроено правильно, бот появится онлайн в Discord.

7. **Использование**  
   - Используйте команду `!start` в текстовом канале, чтобы начать игру, и следуйте инструкциям бота.

## Лицензия

Этот проект распространяется под лицензией MIT. Вы можете свободно использовать, изменять и распространять код при условии указания авторства.

```
MIT License

Copyright (c) 2025 KDG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---
