
import json
import requests
import botogram

TOKEN = ""  # enter the token from botfather..
bot = botogram.create( TOKEN )

@bot.command("hello")
def hello_command(chat, message, args):
    """Say hello to the world!"""
    chat.send("Hello Buddy..😄")
    chat.send("Try </getbusses 17159> </getbusses bustopcode> to see the list of available busses at your bus stop..")

@bot.callback("_get_bus_")
def delete_callback(query, chat, message,data):    
    datalist = data.split(":")
    bus_no = datalist[0]
    bus_stop_code = datalist[1]
    status, next_bus_ = nextBus(bus_stop_code,bus_no)

    if status:
        if next_bus_:
            chat.send(f"Bus Number : {bus_no}")
            for index,item in enumerate(next_bus_):
                msg = f"{index} : Next bus '{bus_no}'is at : {item} 😄"
                chat.send(msg)
        else:
            chat.send(f"☹ Bus '{bus_no}' is not available now. ")
    else:
        chat.send(next_bus_)
    query.notify("you clicked "+data)
    
@bot.command("getbusses")
def getbuses_command(chat, message, args):
    """I will list the busses in this busstop """
    try:
        if len(args)==1:
            print(len(args))
            bstop_code = args[0]
            bus_list = getBusses(bstop_code)
            btns = botogram.Buttons()
    
            if len(bus_list )>0:
                msg='Busses: '
                for index,bus in enumerate(bus_list):
                    btns[index].callback(bus , "_get_bus_",bus+":"+bstop_code)
                    msg = msg + bus +" , "
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
            if status:
                if next_bus_:
                    chat.send(f"Bus Number : {bus_no}")
                    for index,item in enumerate(next_bus_):
                        msg = f"{index} : Next bus '{bus_no}'is at : {item} 😄"
                        chat.send(msg)
                    btns[0].callback("Bye..","goodbye")
                else:
                    chat.send(f"☹ Bus '{bus_no}' is not available now. ")
            else:
                chat.send(next_bus_)
        else:
            chat.send("Bus stop code followed by Bus_Number is required..☹ Try calling '/getnextbus 17159 183'")
    except Exception as e:
        print (e.__doc__)
        chat.send ("Something went wrong...☹ Bus stop code followed by Bus_Number is required..Try calling '/getnextbus 17159 183'")

# **************************************************************************************************

def getresult(bus_stop):
    acc_key =''  # your apikey From DATAMALL
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
    print(result)
    dic={}
    if status:
        for item in result["Services"]:
            listtemp = []
            if "NextBus" in item:
                if item["NextBus"]["EstimatedArrival"] :
                    listtemp.append( item["NextBus"]["EstimatedArrival"].split('T')[1].split("+")[0])

            if "NextBus2" in item:
                if item["NextBus2"]["EstimatedArrival"]:
                    listtemp.append( item["NextBus2"]["EstimatedArrival"].split('T')[1].split("+")[0])

            if "NextBus3" in item:
                if item["NextBus3"]["EstimatedArrival"]:
                    listtemp.append(item["NextBus3"]["EstimatedArrival"].split('T')[1].split("+")[0])
            dic[item["ServiceNo"]]=listtemp
        return True, dic.get(str(bus_no),False) 
    else:
        return False , f"☹ Invalid bustop code : {bus_stop_code}"
    
# **************************************************************************************************
    

if __name__ == "__main__":
    bot.run()
