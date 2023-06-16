import spacy
import pandas as pd
import requests
from bs4 import BeautifulSoup

import yfinance as yf
import streamlit as st

st.title("Buzzing Stocks :zap:")

nlp = spacy.load("en_core_web_sm")


def extract_text_from_rss(rss_link):
    '''
    parse the xml and extract the headings 
    from the links in a python list
    '''
    headings = []
    # default rss_link is from economic times: markets
    r1 = requests.get("https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms")
    # user provided rss_link
    r2 = requests.get(rss_link)
    soup1 = BeautifulSoup(r1.content, features='lxml')
    soup2 = BeautifulSoup(r2.content, features='lxml')
    headings1 = soup1.findAll('title')
    headings2 = soup2.findAll('title')
    headings = headings1 + headings2
    return headings


# Extract all the stock info
def generate_stock_info(headings):
    '''
    Goes over each heading to find out the entities and link it with 
    the nifty 500 companies and extract the market data using yahoo finance ticker function.

    Return: data frame containing all the buzzing stocks and their stats
    '''
    stock_info_dict = {
        'Org': [],
        'Symbol': [],
        'currentPrice': [],
        'dayHigh': [],
        'dayLow': []
        # 'forwardPE':[],
        # 'dividendYield':[]
    }
    stocks_df = pd.read_csv("./data/ind_nifty500list.csv")
    for title in headings:
        doc = nlp(title.text)
        # print(doc)
        for ent in doc.ents:
            try: 
                # checking if entity form doc.ents is present in knowledge base
                if stocks_df['Company Name'].str.contains(ent.text).sum():
                    symbol = stocks_df[stocks_df['Company Name'].str.\
                                       contains(ent.text)]['Symbol'].values[0]
                    # print(symbol) # debugging
                    org_name = stocks_df[stocks_df['Company Name'].str.\
                                       contains(ent.text)]['Company Name'].values[0]
                    
                    # sending yfinance the symbol for stock info
                    stock_info = yf.Ticker(symbol+".NS").info
                    # print(stock_info)
                    stock_info_dict['Org'].append(org_name)
                    stock_info_dict['Symbol'].append(symbol)

                    stock_info_dict['currentPrice'].append(stock_info['currentPrice'])
                    stock_info_dict['dayHigh'].append(stock_info['dayHigh'])
                    stock_info_dict['dayLow'].append(stock_info['dayLow'])
                    # stock_info_dict['forwardPE'].append(stock_info['forwardPE'])
                    # stock_info_dict['dividendYield'].append(stock_info['dividendYield'])
                    # print(stock_info_dict) # debugging
                    # some companies will be missed, 
                    # but we don't need all the info but correct info
                else:
                    pass
            except:
                pass
    
    # debugging # figured out that forwardPE and dividend yield values are not coming in for all.
    arrayLength = {k:len(stock_info_dict[k]) for k in stock_info_dict.keys()}
    print(arrayLength)
    
    output_df = pd.DataFrame(stock_info_dict)
    # print(output_df)
    return output_df


# Add an input field to pass the RSS link
user_input = st.text_input("Add your RSS link here!", "https://www.moneycontrol.com/rss/buzzingstocks.xml")

# Get financial headlines
fin_headings = extract_text_from_rss(user_input)
# print(fin_headings)

# output financial info
output_df = generate_stock_info(fin_headings)
output_df.drop_duplicates(inplace=True)
st.dataframe(output_df)


# display the headlines as well
with st.expander("Expand for financial stocks news!"):
    for heading in fin_headings:
        st.markdown("* " + heading.text)