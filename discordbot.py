# -*- coding: utf-8 -*-
import json
import discord
import ccxt

# ==================================================
# DiscordBOTのトークンID
token = 'your id'

# 取引所のAPIキー
apikey_dict = {'bitmex': 'your id', 'bitflyer': 'your id'}

# 取引所のシークレットキー
apisecret_dict = {'bitmex': 'your id', 'bitflyer': 'your id'}

# 取引所の利用通貨
symbol_dict = {'bitmex': 'BTC/USD', 'bitflyer': 'FX_BTC_JPY'}

# ==================================================

# 初期値
exchange = ccxt.bitmex()
exchange.apiKey = apikey_dict['bitmex']
exchange.secret = apisecret_dict['bitmex']
symbol = symbol_dict['bitmex']

def change_exchange(new_exchange):
	'''
	取引所の変更
	'''
	global exchange
	try:
		exchange = eval('ccxt.' + new_exchange + '()')
		exchange.apiKey = apikey_dict[new_exchange]
		exchange.secret = apisecret_dict[new_exchange]
		reply = '取引所を{}に変更しました'.format(new_exchange)
		return reply
	except:
		reply = '{}は未対応の取引所です'.format(new_exchange)
		reply += '\n対応取引所：{}'.format(list(apikey_dict.keys()))
		return reply

def get_balance():
	'''
	残高を照会する
	残高が０の通貨は無視する
	'''
	try:
		balance = exchange.fetch_balance()

		# 保有数量の大きい順にソート
		reply = ''
		for key, value in sorted(balance['free'].items(), key=lambda x:x[1], reverse=True):
			if value != 0.0:
				reply += '{}: {}\n'.format(key, value)

		if exchange.name == 'bitFlyer':
			collateral = exchange.private_get_getcollateral()
			reply += 'BTC_FX: {}'.format(collateral['collateral'])

		if exchange.name == 'BitMEX':
			positions = exchange.private_get_position()
			reply += 'position: '
			for position in positions:
				if position['currentQty'] > 0:
					reply += '｜{}_long: {}'.format(position['symbol'], position['currentQty'])
				if position['currentQty'] < 0:
					reply += '{｜}_short: {}'.format(position['symbol'], position['currentQty'])

		return reply
	except Exception as e:
		print(e)
		return '残高照会に失敗しました：{}'.format(e)

def market_order(side, amount):
	try:
		reply = exchange.create_order(symbol=symbol, type='market', side=side, amount=amount)
		return reply
	except Exception as e:
		print(e)
		return e

def limit_order(side, amount, price):
	try:
		reply = exchange.create_order(symbol=symbol, type='limit', side=side, amount=amount, price=price)
		return reply
	except Exception as e:
		print(e)
		return e

def open_order_status():
	try:
		reply = ''
		open_orders = exchange.fetch_open_orders()
		if open_orders == []:
			reply = '現在未約定の注文はありません'
		else:
			for open_order in open_orders:
				reply += '\n 注文ID：{}'.format(open_order['id'])
				reply += '\n symbol：{}'.format(open_order['symbol'])
				reply += '\n side：{}'.format(open_order['side'])
				reply += '\n price：{}'.format(open_order['price'])
				reply += '\n amount：{}'.format(open_order['amount'])
				reply += '\n'
		return reply
	except Exception as e:
		print(e)
		return e

def cancel_order(order_id):
	try:
		cancel = exchange.cancel_order(order_id)
		print(cancel)
		reply = 'ステータス：{}'.format(cancel['status'])
		reply += '\n キャンセル数量：{}'.format(cancel['remaining'])
		reply += '\n 約定数量：{}'.format(cancel['filled'])
		reply += '\n'
		return reply
	except Exception as e:
		print(e)
		return e


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

	# ==================================================
	message_content = str(message.content)
	# ==================================================

	# コマンド一覧
	if message.content.startswith('!help'):
		commands = [' !help ', ' !exchange ', ' !balance ', ' !market ', ' !limit ', ' !order ', ' !cancel ']
		reply = 'コマンド一覧：{}'.format(commands)
		await client.send_message(message.channel, reply)
		
	# 取引所変更
	if message.content.startswith('!exchange'):
		messege_list = message.content.split()
		if len(messege_list) == 1:
			reply = '現在の取引所は{}です。'.format(exchange.name)
			reply += '\n取引所はいつでも変更可能です（例：「!exchange bitflyer」'
		else:
			reply = change_exchange(messege_list[1])
		await client.send_message(message.channel, reply)

	# 残高照会
	if message.content.startswith('!balance'):
		message_balance = get_balance()
		await client.send_message(message.channel, message_balance)

	# 成行注文
	if message.content.startswith('!market'):
		messege_list = message.content.split()
		if len(messege_list) == 1:
			reply = '成行注文が行えます（例：!market buy 100）'
		else:
			reply = market_order(messege_list[1], messege_list[2])
		await client.send_message(message.channel, reply)

	# 指値注文
	if message.content.startswith('!limit'):
		messege_list = message.content.split()
		if len(messege_list) == 1:
			reply = '指値注文が行えます（例：!limit buy 100 7000）'
		else:
			reply = limit_order(messege_list[1], messege_list[2], messege_list[3])
		await client.send_message(message.channel, reply)

	# 注文情報の参照
	if message.content.startswith('!order'):
		reply = open_order_status()
		await client.send_message(message.channel, reply)

	# 注文のキャンセル
	if message.content.startswith('!cancel'):
		messege_list = message.content.split()
		if len(messege_list) == 1:
			reply = '注文のキャンセルが行えます（例：!calcel 注文ID）'
			reply += '\n注文IDは「!order」で確認できます'
		else:
			reply = cancel_order(messege_list[1])
		await client.send_message(message.channel, reply)

client.run(token)