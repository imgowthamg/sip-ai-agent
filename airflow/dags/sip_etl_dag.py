from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import yfinance as yf
import feedparser
import sqlite3
import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

DB_PATH = '/home/user/Desktop/SIP/market_data.db'

def extract_data(**kwargs):
    symbols = ["NIFTYBEES.NS", "RELIANCE.NS", "TATAMOTORS.NS", "HDFCBANK.NS"]
    prices = {}
    for s in symbols:
        ticker = yf.Ticker(s)
        hist = ticker.history(period="1d")
        if not hist.empty:
            prices[s] = round(hist['Close'].iloc[-1], 2)
    
    news_url = "https://news.google.com/rss/search?q=Indian+Stock+Market+Nifty+finance&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(news_url)
    headlines = "\n".join([f"- {e.title}" for e in feed.entries[:3]])
    
    return {'prices': prices, 'news': headlines}

def transform_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_task')
    llm = OllamaLLM(model="phi3.5", temperature=0.1)
    
    template = """
    <|system|>
    You are a Senior Market Analyst. Provide a brief 3-bullet point summary for an SIP investor.
    Then, on the very last line, provide exactly one word for sentiment: Bullish, Bearish, or Neutral.
    Format:
    • [Point 1]
    • [Point 2]
    • [Point 3]
    SENTIMENT: [Word]
    <|end|>
    <|user|>
    Nifty Price: ₹{price}
    News: {news}
    <|end|>
    <|assistant|>
    """
    prompt = PromptTemplate(input_variables=["price", "news"], template=template)
    chain = prompt | llm
    return chain.invoke({"price": data['prices']['NIFTYBEES.NS'], "news": data['news']}).strip()

def load_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract_task')
    ai_msg = ti.xcom_pull(task_ids='transform_task')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Save timestamp with hour for the new hourly schedule
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute('''
        INSERT OR REPLACE INTO daily_briefings (date, nifty_price, headlines, ai_summary)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, json.dumps(data['prices']), data['news'], ai_msg))
    conn.commit()
    conn.close()

# HOURLY SCHEDULE: Runs every hour at minute 0, from 9 AM to 4 PM, Mon-Fri
with DAG('sip_daily_etl', 
         schedule='0 9-16 * * 1-5', 
         start_date=datetime(2026, 3, 29), 
         catchup=False) as dag:
    
    t1 = PythonOperator(task_id='extract_task', python_callable=extract_data)
    t2 = PythonOperator(task_id='transform_task', python_callable=transform_data)
    t3 = PythonOperator(task_id='load_task', python_callable=load_data)
    t1 >> t2 >> t3
