import praw
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from praw.models import MoreComments
import pandas as pd
import concurrent
import threading
import time
import logging
import numpy as np
from tqdm import tqdm
from nltk.tokenize import word_tokenize
import multiprocessing
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, losses, Sequential
from tqdm import tqdm
from sklearn.metrics import mean_squared_error 
import json
import pickle
import gensim
#Load Tickers
with open('tickers.pkl', 'rb') as f:
    tickers = pickle.load(f)
tickers = [{'ticker': f' {ticker} ', 'occur': 0} for ticker in tickers]
tickers = pd.DataFrame(tickers)

#Reddit Info
client_id = 'FD6fGd4uEID1MQ'
client_secret = 'PVC2kUrAcVVrn0GvT5EUAtesXR5_WQ'
user_agent = 'scrapeWSB'
#Webdriver setup
fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.set_headless()
#Start Drivers
reddit = praw.Reddit(client_id=client_id, client_secret = client_secret, user_agent = user_agent)
driver = webdriver.Firefox(executable_path='./geckodriver', firefox_options= fireFoxOptions)
#Declare Banned Words (cause im too lazy to do this the right way)
banned = ['ABLE', 'FLEX', 'BOTH', 'LOW', 'TELL', 'FIND', 'WISH', 'X', 'TRUE', 'MOST', 
        'GAIN', 'RSI', 'HOPE', 'A', 'ON', 'FOR', 'IT', 
        'BE', 'AT', 'ALL', 'WHEN', 'INTO', 'SO', 'OR', 
        'NOW', 'MAKE', "AN", 'HAS', 'SEE', 'BEEN', 'BY', 
        'GO', 'SOME', 'HE', 'CAP', 'LOVE', 'AM',
        'ANY', 'ELSE', 'TECH', 'FREE', 'POST', 'NEXT', 'MAN', 
        'WAKE', 'HOME', 'U', 'PM', 'AGO', 'LIFE', 
        'EVER', 'ATH', 'BIG', 'PUMP', 'KIDS', 'CAR', 'OPEN']
banned = [f' {x} ' for x in banned]

MAX_LEN = 399
WORD_DEPTH = 300


model = Sequential()
model.add(layers.Conv1D(4, 100, activation='relu', input_shape = (MAX_LEN, WORD_DEPTH)))
model.add(layers.MaxPool1D())
model.add(layers.Dropout(0.5))
model.add(layers.Flatten())
model.add(layers.Dense(100))
model.add(layers.Dense(1, activation = 'tanh'))
model.build()
model.load_weights('model.h5')


w2v = gensim.models.KeyedVectors.load_word2vec_format('w2vFile')

#Helper Fxns
def check_banned(x):
    if x not in banned:
        return x

#Database
class database():
    def __init__(self, tick):
        self.tickers = tick
        # self._lock = threading.Lock()
    def update(self, post):
        for index, col in self.tickers.iterrows():
            if col['ticker'] in post:
                print(post) 
                local_copy = self.tickers.loc[index, 'occur']
                local_copy += 1
                # time.sleep(0.1)
                self.tickers.loc[index, 'occur'] = local_copy



def get_posts():
    driver.get('https://www.reddit.com/r/wallstreetbets/search?q=flair_name%3A%22Daily%20Discussion%22&restrict_sr=1&sort=new')

    html_class = 'SQnoC3ObvgnGjWt90zD9Z'

    links  = [discussion.get_attribute('href') for discussion in driver.find_elements_by_class_name(html_class)]




    def get_comments(discussion):
        sub = reddit.submission(url = discussion)
        comments = list()
        for post in sub.comments:
            if isinstance(post, MoreComments):
                continue
            comments.append([post.body, post.score, post.id, post.subreddit, post.created])

        return pd.DataFrame(comments,columns=['text', 'score', 'id', 'subreddit', 'created']) 
    posts = list()
    for disc in links:
        posts.append(get_comments(disc))
    return posts






def getMostPopular(numStocks, posts):
    db = tickers 
    for post in tqdm(posts):
        for idx, tick in tickers.iterrows():
            if tick['ticker'] in post:
                db.loc[idx, 'occur'] = db.loc[idx, 'occur'] + 1 
    print('-'*100) 
    print(db[db['occur'] != 0])
    print('-'*100) 
    sorted_tickers = db.sort_values(by = 'occur', axis = 0, ascending=False)
    mask = sorted_tickers['ticker'].apply(check_banned)
    mask = mask.dropna()
    dicts = [sorted_tickers[sorted_tickers['ticker'] == ticker].to_dict() for ticker in mask]
    return [{'ticker': list(a['ticker'].values())[0], 'occur': list(a['occur'].values())[0]} for a in dicts][:10]


def pad(x):
    if x.shape[0] < MAX_LEN:
        padding = np.zeros([MAX_LEN - x.shape[0], 300])
        x = np.concatenate([x, padding])
        return x
    else:
        return x



def getSentiment(data, selected):
    # data = pd.DataFrame({'text':data})
    
    scores = dict()
    
    for tick in selected:
        data = data[tick in data]
        scores.update({tick : 0}) 
    data['text'] = data['text'].apply(lambda x: x.lower())
    data['text'] = data['text'].apply(lambda x: word_tokenize(x))
    data['text'] = data['text'].apply(lambda x: w2v.wv[x])
    data['text'] = data['text'].apply(pad)
    data['sentiment'] = data['text'].apply(lambda x: model.predict(x))


    for idx, d in data.iterrows():
        for tick in selected:
            if tick in d['text']:
                scores.update({tick: scores[tick] + float(data['sentiment']) })

    
    return scores






print("Loading Data")
posts = get_posts()
combined_posts = list()
for post in posts:
    combined_posts += post['text'].to_list()
print("Finding Popularity")
topten = getMostPopular(10, combined_posts)
print("Finding Sentiment")
sentiment = getSentiment(posts, topten)
data = {
    "topTen": topten,
    "sentiment": sentiment
}
with open('data.json', 'w') as f:
    json.dump(data, f)