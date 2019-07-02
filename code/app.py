"""
Routes and views for the flask application.
"""

from flask import Flask, render_template, request, url_for
from web3 import Web3, eth, HTTPProvider
import time
import datetime
import contract_abi

contract_address = "0x8603503Cc5B805e43Bf9E6d3aEE6A67870FeCD98"
w3 = Web3(HTTPProvider('http://localhost:8545'))
contract = w3.eth.contract(address = contract_address, abi = contract_abi.abi)

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='FairChain Home'
    )

@app.route('/add_item')
def add_item():
    return render_template(

	'add_item.html',
        message='Add an Item to the Blockchain.'
    )

@app.route('/item_added', methods = ['POST'])
def item_added():
	if request.method == 'POST':
		sk = request.form['sk']
		address = request.form['address']
		barcode = request.form['barcode']
		amount = request.form['amount']
		price = request.form['price']
		
		nonce = w3.eth.getTransactionCount(address)
		txn_dict = contract.functions.addItem(int(amount), int(barcode), int(price)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"


		return render_template(
			'item_added.html',
			barcode = barcode,
			amount = amount,
			price = price
		)

@app.route('/buy_item')
def buy_item():
	return render_template(
		'buy_item.html',
		message='Buy an Item'
	)

@app.route('/item_bought', methods = ['POST'])
def item_bought():
	if request.method == 'POST':
		sk = request.form['sk']
		buyer_address = request.form['buyer_address']
		seller_address = request.form['seller_address']
		barcode = request.form['barcode']
		amount = request.form['amount']
		
		price = int(contract.functions.getPrice(seller_address, int(barcode)).call())
		total_price = price * int(amount)
		
		nonce = w3.eth.getTransactionCount(buyer_address)
		txn_dict = contract.functions.buyItem(seller_address, int(barcode), int(amount)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'value': total_price,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"


		return render_template(
			'item_bought.html',
			barcode = barcode,
			amount = amount,
			price = price,
			address = seller_address,
			total = total_price
		)
	
@app.route('/delete_item')
def delete_item():
	return render_template(
		'delete_item.html',
		message='Delete an Item'
	)

@app.route('/item_deleted', methods = ['POST'])
def item_deleted():
	if request.method == 'POST':
		sk = request.form['sk']
		address = request.form['address']
		barcode = request.form['barcode']
		amount = request.form['amount']
		
		nonce = w3.eth.getTransactionCount(address)
		txn_dict = contract.functions.deleteItem(int(barcode), int(amount)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"
			
		amount_remaining = contract.functions.getAmount(address, int(barcode)).call();

		return render_template(
			'item_deleted.html',
			barcode = barcode,
			amount = amount,
			amount_remaining = amount_remaining
		)
	
@app.route('/put_item_on_sale')
def put_item_on_sale():
	return render_template(
		'put_item_on_sale.html',
		message='Put an existing item up for sale'
	)
	
@app.route('/item_on_sale', methods = ['POST'])
def item_on_sale():
	if request.method == 'POST':
		sk = request.form['sk']
		address = request.form['address']
		barcode = request.form['barcode']
		amount = contract.functions.getAmount(address, int(barcode)).call();
		price = contract.functions.getPrice(address, int(barcode)).call();
		
		nonce = w3.eth.getTransactionCount(address)
		txn_dict = contract.functions.putUpForSale(int(barcode)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"
			
		return render_template(
			'item_on_sale.html',
			barcode = barcode,
			amount = amount,
			price = price
		)

@app.route('/take_item_off_sale')
def take_item_off_sale():
	return render_template(
		'take_item_off_sale.html',
		message='Take an existing item off of sale'
	)
	
@app.route('/item_off_sale', methods = ['POST'])
def item_off_sale():
	if request.method == 'POST':
		sk = request.form['sk']
		address = request.form['address']
		barcode = request.form['barcode']
		amount = contract.functions.getAmount(address, int(barcode)).call();
		price = contract.functions.getPrice(address, int(barcode)).call();

		
		nonce = w3.eth.getTransactionCount(address)
		txn_dict = contract.functions.takeDownFromSale(int(barcode)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"
			
		return render_template(
			'item_off_sale.html',
			barcode = barcode,
			amount = amount,
			price = price
		)
		
@app.route('/view_item')
def view_item():
	return render_template(
		'view_item.html',
		message='View the details of an item'
	)
	
@app.route('/return_item', methods = ['POST'])
def return_item():
	address = request.form['address']
	barcode = request.form['barcode']
	price = contract.functions.getPrice(address, int(barcode)).call();
	amount = contract.functions.getAmount(address, int(barcode)).call();
	for_sale = contract.functions.isForSale(address, int(barcode)).call();
	
	return render_template(
		'return_item.html',
		address = address,
		barcode = barcode,
		price = price,
		amount = amount,
		for_sale = for_sale
	)

@app.route('/change_price')
def change_price():
	return render_template(
		'change_price.html'
	)

@app.route('/price_changed', methods = ['POST'])
def price_changed():
	if request.method == 'POST':
		sk = request.form['sk']
		address = request.form['address']
		barcode = request.form['barcode']
		price = request.form['price']
		amount = contract.functions.getAmount(address, int(barcode)).call();
		
		nonce = w3.eth.getTransactionCount(address)
		txn_dict = contract.functions.changePrice(int(barcode), int(price)).buildTransaction({
			'gas': 2000000,
			'gasPrice': w3.toWei('40', 'gwei'),
			'nonce': nonce,
			'chainId':3
		});
		signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=sk)
		txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

		txn_receipt = None
		count = 0
		while txn_receipt is None and (count < 30):
			count += 1
			txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
			print(txn_receipt)
			time.sleep(1.0)

		if txn_receipt is None:
			return "{'status': 'failed', 'error': 'timeout'}"
		
		
			
		return render_template(
			'price_changed.html',
			barcode = barcode,
			amount = amount,
			price = price
		)
	
if __name__ == '__main__':
	app.run(debug=True)