import json
import requests
import botogram
from datetime import datetime

TOKEN = "enter your bot token here.. "
# get the token ...
bot = botogram.create( TOKEN )

type_of_loads = {
    "SEA": "Seats Available",
    "SDA": "Standing Available",
    "LSD":"Limited Standing"
    }
type_of_bus = { 
    "SD" : "SD.png",
    "DD":"DD.png",
    "BD":"BD.png"
    }

@bot.command("hello")
def hello_command(chat, message, args):
    """Say hello to the world!"""
    btns = botogram.Buttons()
    chat.send("Hello Buddy..😄")
    chat.send("I am Your SG Bus Assistant. You can ask for timings of Buses.")
    chat.send("Try sending, </getbusses 17159> </getbusses bustopcode> to see the list of available busses at your bus stop..")
    # chat.send_photo('logo.png', caption="Hello ....",)
    chat.send_sticker('logo.png')

@bot.callback("_get_bus_")
def delete_callback(query, chat, message,data):   
    datalist = data.split(":")
    bus_no = datalist[0]
    bus_stop_code = datalist[1]
    status, next_bus_ = nextBus(bus_stop_code,bus_no)
    sendchathandler (status,next_bus_, chat,bus_no )
    query.notify("you clicked "+data)
    
@bot.command("getbusses")
def getbuses_command(chat, message, args):
    """I will list you the busses in this busstop """
    try:
        if len(args)==1:
            print(len(args))
            bstop_code = args[0]
            bus_list = getBusses(bstop_code)
            btns = botogram.Buttons()
    
            if len(bus_list )>0:
                msg='Here you go. Choose the Bus Number You are looking for.'
                for index,bus in enumerate(bus_list):
                    btns[index].callback(bus , "_get_bus_",bus+":"+bstop_code)
                    # msg = msg + bus +" , "
                chat.send(msg, attach=btns)
            else:
                chat.send(f"Invalid bus-stop-code : {bstop_code} ☹")
        else:
            chat.send("Bus stop code required..☹ Try calling '/getbusses 17159'")
    except Exception as e:
        print (e.__doc__)
        chat.send( "Something went wrong..☹ Try calling '/getbusses 17159'")

@bot.command("getnextbus")
def getnextbus_command(chat, message, args):
    """I will provide you with the next available bus timing"""
    try:
        print(len(args))
        if len(args)==0:
            chat.send("Bus stop code and bus_number required.☹ Try calling '/getnextbus 17159 183'")
        elif len(args)==1:
            chat.send("Bus_number required.☹ Try calling '/getnextbus 17159 183'")
        elif len(args)==2:
            bus_no = args[1]
            bus_stop_code = args[0]
            status, next_bus_ = nextBus(bus_stop_code,bus_no)
            btns=botogram.Buttons()
            sendchathandler (status,next_bus_, chat , bus_no)
        else:
            chat.send("Bus stop code followed by Bus_Number is required..☹ Try calling '/getnextbus 17159 183'")
    except Exception as e:
        print (e.__doc__)
        chat.send ("Something went wrong...☹ Bus stop code followed by Bus_Number is required..Try calling '/getnextbus 17159 183'")

# **************************************************************************************************

def getresult(bus_stop):
    acc_key ='DATAMALL API KEY'
    header = { 'AccountKey' : acc_key,
     'accept' : 'application/json'}

    path=f'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={bus_stop}'
    resp = requests.get(path,headers=header)
    if resp.ok and len(resp.json().get("Services")) > 0:
        print("valid bus stop code ...")
        result = resp.json()
        return True,result
    else:
        print("invalid bus stop code ...")
        return False, ''

def getBusses(bus_stop):
    status,result = getresult(bus_stop)
    if status:
        bus_list =[]
        for item in result["Services"]:
            bus_list.append(item["ServiceNo"])
        return bus_list
    else:
        return []

def nextBus(bus_stop_code, bus_no):
    status,result = getresult(bus_stop_code)
    dic={}
    if status:
        for item in result["Services"]:
            listtemp = []
            for key, value in item.items():
                if isinstance(value, dict):
                    _item = item[key]
                    if _item.get("EstimatedArrival", False): 
                        listtemp.append( {
                            "EstimatedArrival":_item["EstimatedArrival"],
                            "Load":_item["Load"],
                            "Type":_item["Type"],
                            } )
            dic[item["ServiceNo"]]= listtemp
        return True, dic.get(str(bus_no),False) 
    else:
        return False , f"☹ Invalid bustop code : {bus_stop_code}"

def message_based_on_time_difference(time):
    time_utc = datetime.fromisoformat(time)
    minutes , seconds = divmod((time_utc - datetime.now(time_utc.tzinfo)).total_seconds(), 60)
    print(minutes,",", seconds)
    if minutes <= 1:
        return ("Arriving Now")
    else:
        return (f"Will be arriving in {int(minutes)} minutes")

def sendchathandler (status,next_bus_, chat,bus_no ):
    if status:
        if next_bus_:
            chat.send(f"Bus Number : {bus_no}")
            for index,item in enumerate(next_bus_):
                message = message_based_on_time_difference(item["EstimatedArrival"])
                busload = item["Load"]
                bustype = item["Type"] 
                chat.send(f"{index+1} : {message} 😄")
                # chat.send(f'{type_of_loads.get(busload,"")}')
                chat.send_sticker(type_of_bus.get(bustype,"logo.png"))   
        else:
            chat.send(f"☹ Bus '{bus_no}' is not available now. ")
    else:
        chat.send(next_bus_)

# **************************************************************************************************
    
if __name__ == "__main__":
    bot.run()
