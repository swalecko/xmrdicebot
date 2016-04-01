#!/usr/bin/python


import sys

#------------LINUX------------------#
#uncomment the following line if you are using Linux
sys.path.append('/usr/local/lib/python3.5/dist-packages')
#-----------------------------------#

import os
import time
import datetime
import json
import requests
import random
import smtplib
import base64
import getpass


#set the Environment variable for the python module library
#############################################################

#set the gmail password for email alerting. Either during execution of this script or hardcoded
password = getpass.getpass()
#password = ""

#Comment or uncomment 
#betSize = float(input("Enter the starting bet amount (min. 0.0001 XMR): "))
betSize = 0.0001
#winAmount = float(input("Enter the desired win amount: "))
winAmount  = 0.0004


#create a process id file (pid) to prevent concurrent running of this script
pid = str(os.getpid())

#set the files for current profit monitoring and logging
#------------LINUX------------------#
pidfile = "/home/pipc/dicebet.pid"
curProfitfile = "/home/pipc/curProfit.txt"
xmrLog = "/home/pipc/dicebot.log"
#------------WINDOWS----------------#
#pidfile = "C:\Projekte\monerodiceBOT\logs\dicebet.pid"
#curProfitfile = "C:\Projekte\monerodiceBOT\logs\CurProfit.txt"
#xmrLog = "C:\Projekte\monerodiceBOT\logs\dicebot.log"
#-----------------------------------#

#receiver email address for reporting
emailaddr = "swalecko@gmail.com"

baseBalance = float(0.3)

#set the bet interval in seconds
interval = 0

#Set the bet size limit!
betSizeLimit = 5


#Let the betCount at 1
#betCount = int(raw_input("Enter the bet count(int): "))
betCount = 1

urlTicker = "https://www.cryptonator.com/api/ticker/xmr-usd"
urlBet = "https://monerodice.net/api/bet"
public_key = ""
private_key = ""
##############################################################

#set the timestamp
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S >> ')

#check if pid file is available, if yes exit this script
if os.path.isfile(pidfile):
	print (pidfile + " already exists, exiting \n")
	with open(xmrLog,"a") as myfile:
					myfile.write(st)
					myfile.write(pidfile +" already exists, exiting")
					myfile.write('\n')
					myfile.close()
	sys.exit()
open(pidfile, 'w').write(pid)



try:

	#Variable for betting and balance request
	repeatBetCount = betCount
	betSizeDefault = betSize
	betWinDefault = betSize*2
	betWin = betSize*2
	countFalse = 0
	countTrue = 0
	lastBetSize = 0

	#simple bet with minimum amount to get the current balance
	try:
		
		jBet = {'public_key': public_key, 'private_key': private_key, 'input_bet': 0.0001, 'input_prize': 0.0002, 'input_roll_type': "over" }
		response = requests.post(urlBet, data=jBet, headers={ "Accept": "application/json", "Accept": "gzip" })
		beforeBalance = (json.loads(response.text)['bet_data']['balance'])
	except:
		print ("")
		print ("Error: Could not connect to the monerodice API")
		print ("")
		with open(xmrLog,"a") as myfile:
			myfile.write(st)
			myfile.write("Error: Could not connect to the monerodice API")
			myfile.write('\n')
			myfile.close()
		exit(1)
		
	
	print ("Current Bet Size Limit: " + str(betSizeLimit) + " XMR")

	while True:
		
		try:
						
			for i in range(betCount):
								
				#Random generator to get the roll type "over" or "under"		
				ran = bool(random.getrandbits(1))
						
				#betTurn = "over"
				if ran == True:
					betTurn = "over"
				elif ran == False:
					betTurn = "under"
				

				#Check if a certain bet size is reached and set a waiting timer and randonmly change the roll type				
				if betSize > betSizeDefault*32:  
				#After a loose bet wait for some time to make the next bet
					
					print ("Waiting randomly 1-4 sec until next bet...")
					
					time.sleep(random.randrange(1,4))			
				
				#Send bet request to the monerodice API
				jBet = {'public_key': public_key, 'private_key': private_key, 'input_bet': betSize, 'input_prize': betWin, 'input_roll_type': betTurn }
				response = requests.post(urlBet, data=jBet, headers={ "Accept": "application/json", "Accept": "gzip" })
			
				#Read some values from the json response			
				afterBetSize = float((json.loads(response.text)['bet_data']['size']))
				afterWon = str((json.loads(response.text)['bet_data']['win']))
				afterBalance = float((json.loads(response.text)['bet_data']['balance']))
				
				
				#check if the API values are correct, if quit betting
				if afterBalance < baseBalance:
					print ("WRONG VALUE RETURN from monerodice API! Bye Bye...")
					print ("Last Bet Size: " + str(lastBetSize))
					exit()
				
				
					
				#Query to get the highest bet size				
				if lastBetSize <= afterBetSize:
					lastBetSize = afterBetSize
				
				#Print some informational output to console		
				
				print ("Bet size: " + str(afterBetSize) + " XMR")
				print ("Bet Size Limit: " + str(betSizeLimit) + " XMR")
				print ("Highest Bet Size: " + str(lastBetSize) + " XMR")
				print ("Intentional Profit: " + str(winAmount) + " XMR")
				print ("Current Profit: " + str(float(afterBalance)-float(beforeBalance)) + " XMR")
				print ("My Balance: " + str(afterBalance) + " XMR")
			
				#Write the current profit to a file to see the process while running in background
				with open(curProfitfile,"w") as myfile:
					myfile.write(st)
					myfile.write(str(float(afterBalance)-float(beforeBalance)))
					myfile.write('\n')
					myfile.close()

				betCount = betCount-1
							
				if afterWon == 'False':
					betSize = betSize*2
					betWin = betWin*2
					countFalse = countFalse + 1
					print ("-------------------------------------------")
					
									
					if betSize >= betSizeLimit:
						print ("Bet SIZE LIMIT OF " + str(betSizeLimit) + " XMR REACHED! ABORT BETTING IMMEDIATELY!!")
						print ("###########################################")
						print ("SUMMARY: ")
						print ("Balance before bet: " + beforeBalance + " XMR")
						print ("Balance after bet:  " + afterBalance + " XMR")
						print ("WON/LOOSE amount: " + str(float(afterBalance)-float(beforeBalance)) + " XMR")
						print ("WON count: " + str(countTrue))
						print ("LOOSE count: " + str(countFalse))
						print ("###########################################")
						
						wonloose = str(float(afterBalance)-float(beforeBalance))
						lastBet = betSize/2
						try:
							fromaddr = emailaddr
							toaddrs  = emailaddr
							subject = "Subject: XMRBot LOOSE Report"
							msg = subject + """
							\n
							Date: %s

							SUMMARY:
							
							Balance before bet: %s XMR
							Balance after bet: %s XMR
							WON/LOOSE amount: %s XMR
							Last Bet Size: %s XMR
							""" % (st, beforeBalance, afterBalance, wonloose, lastBet)


							server = smtplib.SMTP('smtp.gmail.com', 587)
							server.starttls()
							server.login(emailaddr, password)
							server.sendmail(fromaddr, toaddrs, msg)
							server.quit()
						

							with open(xmrLog,"a") as myfile:
								myfile.write(st)
								myfile.write("Bet Size of " + str(betSizeLimit) + " XMR reached!")
								myfile.write('\n')
						except:
							with open(xmrLog,"a") as myfile:
								myfile.write(st)
								myfile.write("Unable to send email! <LOOSE REPORT>")
								myfile.write('\n')
								myfile.write(st)
								myfile.write("Bet Size of " + str(betSizeLimit) + " XMR reached!")
								myfile.write('\n')
								myfile.close()
									
						
						exit(1)	
							
				elif afterWon == "True":
					betSize = betSizeDefault
					betWin = betWinDefault
					countTrue = countTrue + 1
					print ("-------------------------------------------")

		#		time.sleep(interval)
			
						
			if str(betCount) == "0":
				if afterWon == "True":
					betCount = repeatBetCount
					if float(afterBalance)-float(beforeBalance) >= winAmount:
						print ("")
						print ("WIN AMOUNT OF " + str(winAmount) + " REACHED!!")
						break
					else:
						continue
				else:
					betCount = 1
					continue
		
		except KeyboardInterrupt: 
			print ("Bet RUN aborted!")
			exit(0.5)		
		except SystemExit:
			exit()
		except:
			time.sleep(1)
			continue
		break

	with open(xmrLog,"a") as myfile:
		myfile.write(st)
		myfile.write(str(lastBetSize))
		myfile.write('\n')
		myfile.close()


	try:
		tickerResponse = requests.post(urlTicker, headers={ "Accept": "application/json" })
	except:
		print ("")
		print ("Error: Could not connect to the cryptonator API to get the XMR/USD prize")
		
		
	try:
		prize = str(json.loads(tickerResponse.text)['ticker']['price'])
	except:
		prize = "N/A"
		print ("Error: Could not set the prize variable")
		print ("")
		
	wonloose = str(float(afterBalance)-float(beforeBalance))
	strCountTrue = str(countTrue)
	strCountFalse = str(countFalse)
	strLastBetSize = str(lastBetSize)

		
	print ("###########################################")		
	print ("SUMMARY: ")
	print
	try: 
		print ("XMR/USD prize: " + prize + " $")
	except:
		print ("Error: Could not print the prize!")
		
	print ("Balance before bet: " + beforeBalance + " XMR")
	print ("Balance after bet:  " + str(afterBalance) + " XMR")
	print ("WON/LOOSE amount: " + wonloose + " XMR")
	print ("WON count: " + strCountTrue)
	print ("LOOSE count: " + strCountFalse)
	print ("Highest Bet Size: " + strLastBetSize + " XMR")
	print ("###########################################")




	fromaddr = emailaddr
	toaddrs  = emailaddr
	subject = "Subject: XMRBot WIN Report"
	msg = subject + """
	\n
	Date: %s

	SUMMARY:
	XMR/USD prize: %s $
	Balance before bet: %s XMR
	Balance after bet: %s XMR
	WON/LOOSE amount: %s XMR
	WON count: %s
	LOOSE count: %s
	Highest Bet Size: %s XMR
	""" % (st, prize, beforeBalance, afterBalance, wonloose, strCountTrue, strCountFalse, strLastBetSize)

	try:
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(emailaddr, password)
		server.sendmail(fromaddr, toaddrs, msg)
		server.quit()
	except:
		with open(xmrLog,"a") as myfile:
			myfile.write(st)
			myfile.write("Unable to send email! <WIN REPORT>")
			myfile.write('\n')
			myfile.close()

#Delete the pid file
finally:
	os.unlink(pidfile)
