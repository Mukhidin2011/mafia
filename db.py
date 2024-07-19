import sqlite3
from random import shuffle

def players_amount():
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM players"
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return len(rows)

def get_mafia_usernames():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = "SELECT username FROM players WHERE role = mafia"
    cursor.execute(sql)
    data =  cursor.fetchall()
    con.close()
    names = ''
    for row in data:
        names += row[0] + '/n'
    return names

def get_mafia_roles():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = "SELECT player_id, role from players"
    cursor.execute(sql)
    data =  cursor.fetchall()
    con.close()
    names = ''
    return data

def get_all_alive():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = "SELECT useraname from players where dead = 0"
    cursor.execute(sql)
    data =  cursor.fetchall()
    con.close()
    data = [row[0] for row in data]
    return data


def set_roles(players: int) -> None:
    mafias = int(players* 0.3)
    roles = ['mafia'] * mafias +['citizen'] * (players - mafias)
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = "SELECT player_id FROM players"
    cursor.execute(sql)
    data =  cursor.fetchall()
    player_ids = [row[0] for row in data]
    shuffle(roles)
    for role, player_id in zip(roles, player_ids):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = {player_id}"
        cursor.execute(sql)
    con.commit()
    con.close()

def insert_player(player_id: int, username: str) -> None:
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ({player_id}, '{username}')"
    cursor.execute(sql)
    con.commit()
    con.close() 
    
def vote(type, username, player_id):
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    sql = f"SELECT username FROM players WHERE player_id = {player_id} and dead = 0 and voted = 0"
    cursor.execute(sql)
    can_vote = cursor.fetchone()
    if can_vote:
        sql = f"UPDATE players SET {type} = {type} + 1 username = '{username}'"
        cursor.execute(sql)
        sql = f"UPDATE players SET voted = 1  WHERE player_id = {player_id}"
        con.commit()
        con.close()
        return True
    con.close()
    return False
    
def mafia_kill():
    con =  sqlite3.connect("db.db")  
    cur = con.cursor()
    cur.execute(f"SELECT max(mafia_vote) FROM players")
    mafia_voted =cur.fetchone()[0]
    cur.execute(
        f"SELECT COUNT(*) FROM players WHERE dead=  and role = ''")
    mafias = cur.fetchone()[0]
    username_killed  = 'никого'
    if mafias == mafia_voted:
        cur.execute(f"SELECT username FROM players WHERE mafia_vote (max_votes)")
        username_killed= cur.fetchone()[0]
        cur.execute("UPDATE players SET dead 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

print(mafia_kill)


def citizen_kill():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute("SELECT max(citizen_votes) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_votes {max_votes}")
    max_votes = cur.fetchone()[0]
    username_killed =" никого"
    if max_votes == 1:
        cur.execute("SELECT username FROM players WHERE citizen_votes {max_votes}") 
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username {username_killed}*")
        con.commit()
    con.close()
    return username_killed

def check_winner():
    con = sqlite3.connect('db.db')
    cursor = con.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM WHERE role = 'mafia' and dead = 0"
    )
    mafias = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM WHERE role = 'citizen' and dead = 0"
    )
    citizens = cursor.fetchone()[0]
    con.close()
    if mafias == 0:
        return "Горожане"
    if mafias > citizens:
        return "Мафия"
    return None
    
def clear(dead = False):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0"
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit()
    con.close()
    