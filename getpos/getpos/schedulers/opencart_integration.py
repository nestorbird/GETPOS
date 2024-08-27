import requests


def order_integration():
    URL = "https://api.api2cart.com/v1.1/order.list.json?api_key=deceaf85a856a8f07250b889e53f6329&store_key=ed58a22dfecb405a50ea3ea56979360d&customer_email=anil%40yopmail.com&start=0&count=10&params=order_id%2Ccustomer%2Ctotals%2Caddress%2Citems%2Cbundles%2Cstatus"

    response = requests.get(URL)

    print("AAAAAAA",response)
    if response.status_code == 200:

        print('Successful request')

        print('Data:', response.json())

    else:

        print('Error in the request, details:', response.text)