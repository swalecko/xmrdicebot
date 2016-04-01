import json
import requests

#You have to set the public and private key 
urlBet = "https://monerodice.net/api/bet"
jBet = {'public_key': "", 'private_key': "", 'input_bet': 0.0001, 'input_prize': 0.0002, 'input_roll_type': "over" }
response = requests.post(urlBet, data=jBet, headers={ "Accept": "application/json", "Accept": "gzip" })
print (json.loads(response.text)['bet_data']['balance'])







