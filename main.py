from flask import Flask, render_template, request, url_for, redirect
from deck import Deck, Card, PlayersHand
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
goal = 21


class Deck_dblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=False)


# __________________________Saving/updatind data in database_____________________________________________
def saving_data(_id, name, players_deck, players_hand, bot_hand, update=False):
    json_dict = {
        'name': name,
        'players_hand': players_hand,
        'players_deck': players_deck,
        'bot_hand': bot_hand
    }
    data = Deck_dblog(game_id=_id, data=json.dumps(json_dict))
    if update:
        try:
            sql_data = Deck_dblog.query.filter_by(game_id=_id).first()
            sql_data.data = json.dumps(json_dict)
            db.session.commit()
        except Exception as exc:
            print(exc)
    else:
        try:
            db.session.add(data)
            db.session.commit()
        except Exception as exc:
            print(exc)


def receiving_hand(_id):    # Receiving players hand from database
    sql_data = Deck_dblog.query.filter_by(game_id=_id).first()
    return PlayersHand(**json.loads(sql_data.data)['players_hand'])


def receiving_name(_id):    # Receiving players name from database
    sql_data = Deck_dblog.query.filter_by(game_id=_id).first()
    name = json.loads(sql_data.data)['name']
    return name


def receiving_deck(_id):    # Receiving deck from database
    sql_data = Deck_dblog.query.filter_by(game_id=_id).first()
    return Deck(**json.loads(sql_data.data)['players_deck'])


def receiving_bot(_id):    # Receiving computers hand from database
    sql_data = Deck_dblog.query.filter_by(game_id=_id).first()
    return PlayersHand(**json.loads(sql_data.data)['bot_hand'])


def card_drow(_id):     # Pulling 1 card and saving data to database
    name = receiving_name(_id)
    players_hand = receiving_hand(_id)
    deck = receiving_deck(_id)
    bot = receiving_bot(_id)
    card = players_hand.get_card(deck.give_card())
    saving_data(_id, name, deck.to_dickt(), players_hand.to_dickt(), bot.to_dickt(), update=True)
    return card


# ______________________________________ Starting page____________________________________________________
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        name = request.form['name']
        _id = str(uuid4())
        players_deck = Deck()
        player = PlayersHand()
        bot = PlayersHand()
        # _______________________ Pulling 2 cards ___________________________________________________________
        card = player.get_card(players_deck.give_card())
        card2 = player.get_card(players_deck.give_card())
        if card.rank == 'tuz' and card2.rank == 'tuz':
            text = f'{name}, dам выпал {card} и {card2}. Джекпот! вы победили. Поздравляю!'
            return render_template('results.html', text=text, id=_id)
        # _____________________ Bot playing  _____________________________________________________
        bot_status = 'ready to play'
        while bot_status == 'ready to play':  # Bot taking cards till get enough
            bot.get_card(players_deck.give_card())
            print(f'Компьютер берёт карту, {bot.Hand_value} очков')
            if goal >= bot.Hand_value >= 17:  # bot get enough cards
                bot_status = 'enough'
            elif bot.Hand_value > goal:  # Bot lose
                bot_status = 'lose'
        text = f'Ваши карты- {card},{card2}. У вас- {player.Hand_value} очков!'
        saving_data(_id, name, players_deck.to_dickt(), player.to_dickt(), bot.to_dickt())  # Saving data into database
        return redirect(url_for('game', text=text, id=_id, name=name, method='show'))


@app.route('/game', methods=['GET'])
def game():
    _id = request.args.get('id')
    method = request.args.get('method')
    # __________________________________Representing players hand_______________________________
    if method == 'show':
        players_hand = receiving_hand(_id)
        text = f'В вашей руке- {players_hand} , у вас- {players_hand.Hand_value} очков'
    # __________________________________Getting 1 card_________________________________________
    elif method == 'get':
        text = request.args.get('text')
    # __________________________________Representing bot hand__________________________________
    elif method == 'show_bot':
        bot = receiving_bot(_id)
        text = f'В руке бота- {bot} , у него- {bot.Hand_value} очков'
    return render_template('game.html', text=text, id=_id)


@app.route('/get_card', methods=['GET', 'POST'])
def get_card():
    _id = request.args.get('id')
    card = card_drow(_id)
    players_hand = receiving_hand(_id)
    if card.rank == 'tuz' and players_hand.Hand_value > goal:  # If player get Tuz and get too much value
        players_hand.Hand_value -= 10
        text = 'Вам выпал туз и вы перебрали допустимое кол-во очков, поэтому ценность туза изменена на 1' \
               f'вы набрали {players_hand.Hand_value} очков'
        return redirect(url_for('game', text=text, id=_id, method='get'))
    elif players_hand.Hand_value > goal:  # Player get too much value
        text = f'Вам выпала карта {card}. Вы набрали {players_hand.Hand_value} очков и проиграли :('
        return render_template('results.html', text=text, id=_id)
    else:
        text = f'Ваша карта- {card}, у вас- {players_hand.Hand_value} очков'
        return redirect(url_for('game', text=text, id=_id, method='get'))


@app.route('/results', methods=['GET', 'POST'])
def results():
    _id = request.args.get('id')
    players_hand = receiving_hand(_id)
    bot = receiving_bot(_id)
    if players_hand.Hand_value > bot.Hand_value or bot.Hand_value > goal:
        text = f'Ваши карты: {players_hand}. Вы набрали {players_hand.Hand_value} очков. \n' \
               f'У компьютера {bot}. Компьютер набрал {bot.Hand_value} очков! Вы победили!'
    else:
        text = f'Ваши карты: {players_hand}. Вы набрали {players_hand.Hand_value} очков. \n' \
               f'У компьютера {bot}. Компьютер набрал {bot.Hand_value} очков! Вы проиграли :('
    return render_template('results.html', text=text, id=_id)


if __name__ == '__main__':
    app.run(debug=True)
