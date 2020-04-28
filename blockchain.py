# -*- coding: UTF-8 -*-
# 一个区块的结构
# {
#     "index":0,
#     "timestamp":"",
#     "transactions":[
#       {
#         "sender":"",
#         "recipient":"",
#         "amount":5
#       }
#     ],
#     "proof":"",
#     "previous_hash":""
# }
import hashlib
import json
import socket
from time import time
from uuid import uuid4

from flask import Flask, jsonify
from flask import request


class BlockChain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #    建立一个创世区块
        self.new_block(proof=100, previous_hash=1)

    # 建立一个新的区块
    def new_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or (self.chain[-1]["hash"])
        }
        block["hash"] = self.hash(block)
        self.current_transactions = []
        self.chain.append(block)
        return block

    # 建立一个新的交易
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
            {
                "sender": sender,
                "recipient": recipient,
                "amount": amount
            }
        )
        return self.last_Block["index"] + 1

    # 计算区块hash
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    # 最后一个区块
    @property
    def last_Block(self):
        return self.chain[-1]

    # pow
    def proof_of_work(self, last_proof: int) -> int:
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        print(proof)
        return proof

    # pow
    def valid_proof(self, last_proof: int, proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # print(last_proof)
        # print(guess)
        print(guess_hash)
        if guess_hash[0:4] == '0000':
            return True
        else:
            return False

#
# testPow = BlockChain()
# testPow.proof_of_work(100)
# testPow.new_transaction("axe","pom",5)
# print(testPow.chain)
# print(testPow.current_transactions)



app = Flask(__name__)
blockchain = BlockChain()
node_id  = str(uuid4()).replace('-','')
@app.route('/',methods=['GET'])
def hello():
    return 'hello blockchain'

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    # 建立一个新的交易并插入到current_transaction中
    values = request.get_json()
    required = ["sender","recipient","amount"]
    if values is None:
        return "Missing Values", 400
    if not all  (k in values for k in required):
        #       k里面有一个不在required里面  if就成立
        return "Missing Values",400
    index = blockchain.new_transaction(values["sender"],values["recipient"],values["amount"])
    response = {"massage":f'Transaction will be add to block {index}'}
    return jsonify(response),201


@app.route('/mine',methods=['GET'])
def mine():
    last_block  = blockchain.last_Block
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender='0',recipient=node_id,amount=1)
    block = blockchain.new_block(proof,None)
    response = {"massage":"New Block Forged",
                "index":block["index"],
                "transaction":block["transactions"],
                "proof":block["proof"],
                "previous_hash":block["previous_hash"]
                }
    return jsonify(response),200
@app.route('/chain',methods=['GET'])
def full_chain():
    # 返回区块链信息给请求者
    response = {
        "chain":blockchain.chain,
        "length":len(blockchain.chain)
    }
    # return 可能有错 jsonify
    return jsonify(response),200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)


