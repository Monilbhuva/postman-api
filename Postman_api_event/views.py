from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import http.client
import socket
import requests
import uuid
import json
from http.client import HTTPSConnection
from homepage_stock_list.models import Homepage_stock_list
import mimetypes
from django.http import JsonResponse
from datetime import datetime, timedelta  



api_key = 'TJUyGz6L'
username = 'Svca1072'
pwd = 'Monil@24'
mpin = '2424'
smartApi = SmartConnect(api_key)
candleData = 0

    # print('SmartApi :',smartApi)
try:
    token = "KEAPBSVESSOI5EHQLZKYCTSHMU"
    totp = pyotp.TOTP(token).now()
        # print('totp:', totp)
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e
    
correlation_id = "abcde"
data = smartApi.generateSession(username, mpin, totp)
# print(data['data'])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
response = requests.get("https://api.ipify.org?format=json")
global_ip = response.json()["ip"]
mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
authToken = data['data']['jwtToken']
print("local", local_ip)
print("globl", global_ip)
print("mac", mac_address)
print("auth", data)
headers = {
        'X-PrivateKey': api_key,
        'Accept': 'application/json',
        'X-SourceID': 'WEB',
        'X-ClientLocalIP': local_ip,
        'X-ClientPublicIP': global_ip,
        'X-MACAddress': mac_address,
        'X-UserType': 'USER',
        'Authorization': authToken,
        'Content-Type': 'application/json'
}

conn = http.client.HTTPSConnection("apiconnect.angelone.in")  # Replace with actual URL


                

def index(request):
    watch_list_data = Homepage_stock_list.objects.all().values('tradingsymbol', 'symboltoken')
    context = {
        'watchList': list(watch_list_data),  # Convert QuerySet to list of dictionaries
    }
    return render(request, 'index.html', context)

def demo(request):
 
    if data['status'] == False:
        # logger.error(data)
        pass
        
    else:
        # login api call
        # logger.info(f"You Credentials: {data}")
        authToken = data['data']['jwtToken']
        refreshToken = data['data']['refreshToken']
        # fetch the feedtoken
        feedToken = smartApi.getfeedToken()
        # fetch User Profile
        res = smartApi.getProfile(refreshToken)
        smartApi.generateToken(refreshToken)
        res=res['data']['exchanges']
        # print('authtoken:',authToken)
        # print('refreshToken:',refreshToken)
        # print('feedToken:',feedToken)
        # print('name:',data['data']['name'])

    
    #place order
    # try:
    #     orderparams = {
    #         "variety": "NORMAL",
    #         "tradingsymbol": "SBIN-EQ",
    #         "symboltoken": "3045",
    #         "transactiontype": "BUY",
    #         "exchange": "NSE",
    #         "ordertype": "LIMIT",
    #         "producttype": "INTRADAY",
    #         "duration": "DAY",
    #         "price": "19500",
    #         "squareoff": "0",
    #         "stoploss": "0",
    #         "quantity": "1"
    #         }
    #     # Method 1: Place an order and return the order ID
    #     orderid = smartApi.placeOrder(orderparams)
    #     logger.info(f"PlaceOrder : {orderid}")
    #     # Method 2: Place an order and return the full response
    #     response = smartApi.placeOrderFullResponse(orderparams)
    #     logger.info(f"PlaceOrder : {response}")
    # except Exception as e:
    #     logger.exception(f"Order placement failed: {e}")

    #Historic api
    try:
        historicParam={
        "exchange": "NSE",
        "symboltoken": "3045",
        "interval": "ONE_MINUTE",
        "fromdate": "2021-02-08 09:00", 
        "todate": "2021-02-08 09:16"
        }
        # candleData = pd.DataFrame(smartApi.getCandleData(historicParam))
    except Exception as e:
        logger.exception(f"Historic Api failed: {e}")


    conn = http.client.HTTPSConnection("apiconnect.angelone.in")
  





    # Correct the payload by converting it to JSON and then encoding to bytes
    payload = {
        "mode": "FULL",
        "exchangeTokens": {
            "NSE": ["3045"]
        }
    }
    payload = json.dumps(payload).encode('utf-8')  # Convert dict to JSON and then to bytes

    # Define headers
 


    # Create connection
    conn = HTTPSConnection("apiconnect.angelone.in")  # Replace with your API domain if different

    # Send POST request
    conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)

    # Get response
    res = conn.getresponse()
    data2 = res.read()
    print(data2)

    # Return response as HttpResponse
    return HttpResponse(data2)


def profile(request):
    clientData = data['data']
    print("clientData:",clientData)
    return render(request, 'profile.html', {'clientData' : clientData})


def stock_search(request):
    query = request.GET.get('query', '').strip()  # Get the search query
    stock_data = None

    if query:

        payload = json.dumps({
            "mode": "FULL",
            "exchangeTokens": {
                "NSE": [query]  # Using the query directly; ensure it's valid
            }
        })

        conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)
        res = conn.getresponse()
        data2 = res.read().decode('utf-8')  # Decode the byte response to a string
        stock_data = json.loads(data2)['data']['fetched'][0]
        # print()
        current_price = stock_data['ltp']
        difference = current_price - stock_data['close']
        percentage_change = (difference / stock_data['close']) * 100 if stock_data['close'] else 0

        # Add these calculations to the context
        stock_data['difference'] = difference
        stock_data['percentage_change'] = percentage_change
        # Make a request to the Angel API (use the appropriate endpoint)
      
  
        # Get the current date and time
        now = datetime.now()  # Correct usage of datetime.now()

        # Calculate `fromdate` which is current time minus one day (yesterday at the same time)
        fromdate = (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')

        # Format the current `todate` as the current time in the required format
        todate = now.strftime('%Y-%m-%d %H:%M')

        # Prepare the payload for the API request
        payload1 = json.dumps({
            "exchange": "NSE",  # Ensure this is correct for your use case
            "symboltoken": query,  # Correct symbol token
            "interval": "FIVE_MINUTE",  # Correct interval
            "fromdate": fromdate,  # From 1 day before the current time
            "todate": todate  # Current time
        })

        # API call to fetch candlestick data
        conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payload1, headers)
        res1 = conn.getresponse()
        dataCandel = res1.read()
        finalData = dataCandel.decode("utf-8")
        
        # Parse the JSON data
        data_dict = json.loads(finalData)
        candle_data = data_dict.get("data", [])
        
        # Format data for ApexCharts
        formatted_data = [
            {
                "x": datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z").timestamp() * 1000,  # Unix timestamp in milliseconds
                "y": [data[1], data[2], data[3], data[4]]  # [Open, High, Low, Close]
            }
            for data in candle_data
        ]
        # Pass the data to the template


       
        try:
            if stock_data:
                return render(request, 'stock_info.html', {'stock_data': stock_data, 'candle_data': json.dumps(formatted_data)})
            
        except Exception as e:
            logger.exception(f"Order placement failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


def stock_search_detail(request, symboltoken):
    # query = request.GET.get('symboltoken')  # Get the search query
    stock_data = None

    if symboltoken:
        # Make a request to the Angel API (use the appropriate endpoint)
        payload = json.dumps({
            "mode": "FULL",
            "exchangeTokens": {
                "NSE": [symboltoken]  # Using the query directly; ensure it's valid
            }
        })
  
        conn.request("POST", "/rest/secure/angelbroking/market/v1/quote/", payload, headers)
        res = conn.getresponse()
        data2 = res.read().decode('utf-8')  # Decode the byte response to a string
        stock_data = json.loads(data2)['data']['fetched'][0]
        # print()
        current_price = stock_data['ltp']
        difference = current_price - stock_data['close']
        percentage_change = (difference / stock_data['close']) * 100 if stock_data['close'] else 0

        # Add these calculations to the context
        stock_data['difference'] = difference
        stock_data['percentage_change'] = percentage_change



        # Get the current date and time
        now = datetime.now()  # Correct usage of datetime.now()

        # Calculate `fromdate` which is current time minus one day (yesterday at the same time)
        fromdate = (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')

        # Format the current `todate` as the current time in the required format
        todate = now.strftime('%Y-%m-%d %H:%M')

        # Prepare the payload for the API request
        payload1 = json.dumps({
            "exchange": "NSE",  # Ensure this is correct for your use case
            "symboltoken": symboltoken,  # Correct symbol token
            "interval": "THREE_MINUTE",  # Correct interval
            "fromdate": fromdate,  # From 1 day before the current time
            "todate": todate  # Current time
        })

        # API call to fetch candlestick data
        conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payload1, headers)
        res1 = conn.getresponse()
        dataCandel = res1.read()
        finalData = dataCandel.decode("utf-8")

        data_dict = json.loads(finalData)
        candle_data = data_dict.get("data", [])
        
        # Format data for ApexCharts
        formatted_data = [
            {
                "x": datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z").timestamp() * 1000,  # Unix timestamp in milliseconds
                "y": [data[1], data[2], data[3], data[4]]  # [Open, High, Low, Close]
            }
            for data in candle_data
        ]

        try:
            if stock_data:
                return render(request, 'stock_info.html', {'stock_data': stock_data, 'candle_data': json.dumps(formatted_data)})
            
        except Exception as e:
            logger.exception(f"Order placement failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})




def addWatchlist(request):
    # Fetch data from URL parameters
    tradingsymbol = request.GET.get('tradingSymbol')
    symboltoken = request.GET.get('symbolToken')
    # Check if both values exist
    if tradingsymbol and symboltoken:
        # Store the data in the database
        modelOjct = Homepage_stock_list(tradingsymbol=tradingsymbol, symboltoken=symboltoken)
        modelOjct.save()  # Save to the database

        # Optionally redirect or send a success response
        return redirect('index') 
    else:
        # Handle the case where parameters are missing
        return HttpResponse("Invalid data, could not add to watchlist.")
    


def getStockLTP(request):
    tradingsymbol = request.GET.get('tradingsymbol')
    symboltoken = request.GET.get('symboltoken')

    # Example of getting live stock prices from your API
    conn = http.client.HTTPSConnection("apiconnect.angelone.in")
    payload = json.dumps({
        "exchange": "NSE",
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken
    })
    conn.request("POST", "/order-service/rest/secure/angelbroking/order/v1/getLtpData", payload, headers)

    res = conn.getresponse()
    dataLtp = json.loads(res.read().decode('utf-8'))
    orignalData = dataLtp.get('data')
    # Extract LTP and previous close data
    stock_data = {
        "ltp": orignalData['ltp'],
        "close": orignalData['close']
    }
    return JsonResponse(stock_data)


def getWatchList(request):
    watch_list_data = Homepage_stock_list.objects.all().values('tradingsymbol', 'symboltoken')
    # The .values() method returns a queryset as a list of dictionaries with only specified fields.
    return JsonResponse(list(watch_list_data), safe=False)


def deleteStockINwatchList(request, symboltoken):
    # Fetch the stock by symboltoken or return 404 if it doesn't exist
    stock = get_object_or_404(Homepage_stock_list, symboltoken=symboltoken)

    # Delete the stock
    stock.delete()
    return redirect('index')



def buyStock(request):
    if request.method == 'POST':
        # Fetch form data from request
        # exchange = request.POST.get('exchange')
        quantity = request.POST.get('quantity')
        tradingSymbol = request.POST.get('tradingSymbol')
        symbolToken = request.POST.get('symbolToken')
        price = request.POST.get('price')
        # productType = request.POST.get('productType')

  

        # Prepare order parameters dynamically using form data
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": tradingSymbol,  # from form
            "symboltoken": symbolToken,      # from form
            "transactiontype": "BUY",
            "exchange": "NSE",            # from form (NSE/BSE)
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,                  # Update this dynamically if needed
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity             # from form
        }

        # Try to place the order
        try:
            # Place the order and get the order ID
            orderid = smartApi.placeOrder(orderparams)
            logger.info(f"PlaceOrder : {orderid}")
            
            # Return success response with order ID
            return JsonResponse({'success': True, 'order_id': orderid})
        except Exception as e:
            logger.exception(f"Order placement failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



def portfolio(request):

    # Fetch Holdings
    conn.request("GET", "/rest/secure/angelbroking/portfolio/v1/getAllHolding", '', headers)
    holdings_res = conn.getresponse()
    holdings_data = json.loads(holdings_res.read().decode("utf-8"))

    # Fetch Positions
    conn.request("GET", "/rest/secure/angelbroking/order/v1/getPosition", '', headers)
    positions_res = conn.getresponse()
    positions_data = json.loads(positions_res.read().decode("utf-8"))

    context = {
        'portfolio_data': holdings_data,  # Portfolio holdings data
        'position_data': positions_data.get('data', [])  # Positions data as a list
    }
    return render(request, 'portfolio.html', context)


def get_order_book(request):
 

    conn.request("GET", "/rest/secure/angelbroking/order/v1/getOrderBook", '', headers)
    order_book_res = conn.getresponse()
    order_book_data = json.loads(order_book_res.read().decode("utf-8"))

    # Separate orders into Pending, Rejected, and Canceled
    pending_orders = []
    rejected_orders = []
    canceled_orders = []

    for order in order_book_data.get("data", []):
        if order['orderstatus'] == 'rejected':
            rejected_orders.append(order)
        elif order['orderstatus'] == 'pending':
            pending_orders.append(order)
        elif order['orderstatus'] == 'cancelled':
            canceled_orders.append(order)

    # Fetch Executed Orders from Trade Book
    conn.request("GET", "/rest/secure/angelbroking/order/v1/getTradeBook", '', headers)
    trade_book_res = conn.getresponse()
    trade_book_data = json.loads(trade_book_res.read().decode("utf-8"))
    executed_orders = trade_book_data.get("data", [])

    context = {
        'pending_orders': pending_orders,
        'rejected_orders': rejected_orders,
        'canceled_orders': canceled_orders,
        'executed_orders': executed_orders
    }

    return render(request, 'orderbook.html', context)


def candel(request):

    payload = "{\r\n     \"exchange\": \"NSE\",\r\n\"symboltoken\": \"3045\",\r\n     \"interval\":\"ONE_MINUTE\",\r\n  \"fromdate\": \"2024-09-29 09:15\",\r\n \"todate\": \"2024-09-30 15:16\"\r\n}"

    # API call to fetch candlestick data
    conn.request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", payload, headers)
    res = conn.getresponse()
    dataCandel = res.read()
    finalData = dataCandel.decode("utf-8")
    
    # Parse the JSON data
    data_dict = json.loads(finalData)
    candle_data = data_dict.get("data", [])
    
    # Format data for ApexCharts
    formatted_data = [
        {
            "x": datetime.strptime(data[0], "%Y-%m-%dT%H:%M:%S%z").timestamp() * 1000,  # Unix timestamp in milliseconds
            "y": [data[1], data[2], data[3], data[4]]  # [Open, High, Low, Close]
        }
        for data in candle_data
    ]
    print(formatted_data)
    # Pass the data to the template
    return render(request, 'candle_chart copy.html', {'candle_data': json.dumps(formatted_data)})


def sell_order(request):

    if request.method == 'POST':
        # Fetch form data from request
        # exchange = request.POST.get('exchange')
        quantity = request.POST.get('quantity')
        tradingSymbol = request.POST.get('tradingSymbol')
        symbolToken = request.POST.get('symbolToken')
        price = request.POST.get('ltp')
        # productType = request.POST.get('productType')

  

        # Prepare order parameters dynamically using form data
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": tradingSymbol,  # from form
            "symboltoken": symbolToken,      # from form
            "transactiontype": "SELL",
            "exchange": "NSE",            # from form (NSE/BSE)
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": price,                  # Update this dynamically if needed
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity             # from form
        }

        # Try to place the order
        try:
            # Place the order and get the order ID
            orderid = smartApi.placeOrder(orderparams)
            logger.info(f"PlaceOrder : {orderid}")
            return redirect('portfolio')

        except Exception as e:
            logger.exception(f"Order Sell failed: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})