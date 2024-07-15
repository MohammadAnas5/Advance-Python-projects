from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import pandas as pd 

app = Flask(__name__)

url = "https://www.flipkart.com/search?q=mobiles+under+30000&as=on&as-show=on&otracker=AS_Query_OrganicAutoSuggest_4_13_na_na_na&otracker1=AS_Query_OrganicAutoSuggest_4_13_na_na_na&as-pos=4&as-type=RECENT&suggestionId=mobiles+under+30000&requestId=8a04be8e-17ba-491a-b07e-4a82ac357c17&as-searchtext=mobiles%20under"
a = requests.get(url)
x = BeautifulSoup(a.text,"lxml")

nameli = x.find_all("div",class_="_4rR01T")
names = [i.text for i in nameli] 

ratingli = x.find_all('div',class_="_3LWZlK")
rating = [i.text for i in ratingli] 

priceli = x.find_all('div',class_="_30jeq3 _1_WHN1")
price = [i.text for i in priceli]

difr_n = len(rating)- len(names)
difr_p = len(rating)- len(price)
names.extend(" "*difr_n)
price.extend(" "*difr_p)


dic = {'names':names,'Rating':rating,"price":price}
df  = pd.DataFrame(dic)

@app.route('/')
def index():
    # Render the template with DataFrame passed to it
    return render_template('home.html', tables=[df.to_html(classes='data', header="true")])

if __name__ == '__main__':
    app.run()
