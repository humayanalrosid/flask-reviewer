import requests, logging
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ul
from flask_cors import CORS, cross_origin
from pymongo.mongo_client import MongoClient

logging.basicConfig(filename='scrapper.log', level=logging.INFO)

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def home():
    return render_template('home.html')

@app.route('/reviews', methods = ['POST', 'GET'])
def reviews():
    if request.method == 'POST':
        try:
            searchString = request.form['search'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = ul(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            
            flipkart_html = bs(flipkart_page, 'html.parser')
            bigBoxes = flipkart_html.findAll('div', {'class': '_1AtVbE col-12-12'})
            
            del bigBoxes[0:3]
            
            box = bigBoxes[0]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            product_request = requests.get(product_link)
            product_request.encoding = 'UTF-8'
            
            product_html = bs(product_request.text, 'html.parser')
            comment_boxes = product_html.find_all('div', {'class': '_16PBlm'})
            
            reviews = []
            for commentbox in comment_boxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    logging.info("name")
                    
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                    logging.info("rating")
                    
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                    
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    commentHead = 'No Comment'
                    logging.info(e)
 
                reviews_data = {
                    "Product": searchString,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commentHead, 
                    "CommentBody": custComment
                }
                reviews.append(reviews_data)
            logging.info("log my final result {}".format(reviews))
            return render_template('reviews.html', reviews=reviews[0:(len(reviews)-1)])
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    else:
        return redirect('home.html') 

if __name__ == "__main__":
    app.run(debug=True)

