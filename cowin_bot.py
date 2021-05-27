from cowin_api import *
import discord, time, json, os

client = discord.Client()
token = os.getenv("TOKEN")

def fetch_json(fileName):
	with open(const.PATH + fileName) as file:
		if file:
			data = json.load(file)
			return data
		else:
			print('Fetch failed')

def dump_json(fileName, data):
	with open(const.PATH + fileName, 'w') as file:
		json.dump(data, file, indent = 4)

def checkStatus(var):
	logData = fetch_json('data.json') 
	return logData[str(var)]

def setStatus(var, status = True):
	logData = fetch_json('data.json') 
	logData[str(var)] = status
	dump_json('data.json', logData)

def fetch_available_centers(data):
	data = data['centers']
	available_centers = []
	for center in data:
		if center['sessions'][0]['available_capacity'] > 0:
			available_centers.append(center)
	return available_centers

    
@client.event
async def on_ready():
	dateAndTime = datetime.now()
	currentTime = dateAndTime.time()
	print('Discord server started successfully at ' + str(currentTime))


@client.event
async def on_message(message):
	if message.author == client.user:
		return


	if message.content.lower() == '/start':
		try:
			await message.channel.send('Started cowin bot successfully')
			setStatus("start")
			while checkStatus('start'):
				actual = datetime.today()
				list_format = [actual + timedelta(days=i) for i in range(7)]
				actual_dates = [i.strftime("%d-%m-%Y") for i in list_format]
				for date in actual_dates:
					slots_data = get_availability_by_district('4', date)
					data = fetch_json('data.json')
					data['slots'] = slots_data
					dump_json('data.json', data)
					available_centers = fetch_available_centers(slots_data)
					if len(available_centers) > 0:
						await message.channel.send(str(len(available_centers)) + 'available in Krishna district')
						for center in available_centers:
							msg = str(center['sessions'][0]['available_capacity']) + str(center['sessions'][0]['vaccine']) + 'vaccines are available at ' 
							+ center['name'] + ' ' +  center['address'] + ' ' + center['district_name'] + ' ' 
							+ center['block_name'] + ' ' + str(center['pincode']) + ' on ' + center['sessions'][0]['date']
							await message.channel.send(msg)
					time.sleep(30)
		except Exception as e:
			error_msg = e + ' raised at ' + str(datetime.now().strftime("%H:%M:%S"))
			await message.channel.send(error_msg)

	if message.content.lower() == '/stop':
		setStatus("start", False)
		await message.channel.send('Stopped cowin bot successfully')


client.run(token)



