import requests
import datetime
import os
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API = os.environ['STOCK_API']
NEWS_API = os.environ['NEWS_API']


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

date = str(datetime.datetime.now().date()-datetime.timedelta(days=1))
# date = "2022-09-13"

# alpha advantage API
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={STOCK}&apikey={STOCK_API}'
r = requests.get(url)
data = r.json()
price_details = data["Time Series (Daily)"][date]
open_price = price_details['1. open']
open_price = float(open_price)
close_price = price_details["5. adjusted close"]
close_price = float(close_price)

send_email = False

percentage_change = float("%.2f" % round((close_price - open_price)/open_price * 100, 2))

if percentage_change > 0:
    sms_percentage_change = f"🔺 {percentage_change}%"
elif percentage_change < 0:
    sms_percentage_change = f"🔻 {percentage_change}%"
else:
    sms_percentage_change = f"NO Change"


if -2 > percentage_change or percentage_change > 2:

    # STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    news_url = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from={date}&sortBy=popularity&apiKey={NEWS_API}'

    response = requests.get(news_url)
    news = response.json()
    news_list_sms = []
    for _ in range(3):
        news_title = news["articles"][_]['title']
        news_description = news["articles"][_]['description']
        new_list = [news_title, news_description]
        news_list_sms.append(new_list)

    news_sms = ""
    for x in news_list_sms:
        f_string = f"""
        Headline: {x[0]}
        Brief: {x[1]}
        """
        news_sms += f_string

    # STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number.

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']

    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body=f""" {STOCK} {sms_percentage_change}
                         {news_sms}
                         """,
                         from_='+12537931304',
                         to='+61405993935'
                     )

    print(message.sid)
    print("NEWS Sent")
