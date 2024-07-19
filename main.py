from telebot import TeleBot
from time import sleep
import db


TOKEN = '6592242093:AAGGyfNU3oqMLpLj7Rtsu_va8lJLZy6i_GA'
bot = TeleBot(TOKEN)
game = False
night = False

@bot.message_handler(commands = ['play'])
def start(message):
    bot.send_message(message.chat_id, "Если хотите играть напишите 'готов играть' в лс ")

@bot.message_handler(func=lambda m: m.text.lower()== '' and m.chat.type == 'private')
def add_player(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user_i, message.from_user.username)
    

@bot.message_handler(commands=['game'])
def start_game(message):
    global game
    players = db.players_amount()
    if players >= 5:
        db.set_roles (players)
        game = True
        players_roles = db.get_player_roles()
        mafias = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, f'Ваша роль: {role}')
            if role == 'mafia':
                    bot.send_message(player_id, f'Мафия: {mafias}')
        bot.send_message(message.chat.id, "Игра началась")
        db.clear()
        game_loop(message)
        return
    bot.send_message(message.chat.id, 'Недостаточно игроков')
    



@bot.message_handler(commands=["kick"])
def kick(message):
    username = message.text.split()[1]
    usernames = db.get_all_alive()
    if not night:
        if username not in usernames:
            bot.send_message(message.chat.id, "Такого пользователя нет в игре")
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'Вы не можете голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас ночь, нельзя голосовать')


@bot.message_handler(commands=["kick"])
def kick(message):
    username = message.text.split()[1]
    usernames = db.get_all_alive()
    if not night:
        if username not in usernames:
            bot.send_message(message.chat.id, "Такого пользователя нет в игре")
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'Вы не можете голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас ночь, нельзя голосовать')


@bot.message_handler(commands=["kill"])
def kill(message):
    username = message.text.split()[1]
    usernames = db.get_all_alive()
    mafia = db.get_mafia_usernames
    if night:
        if username not in usernames:
            bot.send_message(message.chat.id, "Такого пользователя нет в игре")
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учтен')
            return
        bot.send_message(message.chat.id, 'Вы не можете убивать')
        return
    bot.send_message(message.chat.id, 'Сейчас нельзя убивать')

    

def get_killed(night):
    if not night:
        username_killed = db.citizen_kill()
        return f'Горожане выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'


night = True

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, "Добро пожаловать в игру! Вам дано ә минуты чтобы познакомиться")
    sleep(120)
    while True:
        killed = get_killed(night)
        bot.send_message(message.chat.id, killed)
        if night:
            bot.send_message(message.chat.id, "Город засыпает, просыпается мафия.Наступила ночь.")
        else:
            bot.send_message(message.chat.id, "Город просыпается. НАступил день.")
        night = not night
        winner = db.check_winner()
        if winner:
            bot.send_message(message.chat.id, f'Победили {winner}')
            game = False
            return
        sleep(120)
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f'В игре:\n{alive}')
        sleep(2)


if __name__ == '__main__':
    bot.polling(none_stop = True)