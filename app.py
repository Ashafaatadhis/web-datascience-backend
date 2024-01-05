from flask import Flask, jsonify, request
from flask_cors import CORS
from dto.respBody import GetDto
import json
import pickle
import pandas as pd
import asyncio
from pyppeteer import launch
 




app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# terlalu berat
# anime = pickle.load(open("./movies_list.pkl", "rb"))
# similarity = pickle.load(open("./similarity.pkl", "rb"))

@app.route('/api/')
def get_data():
    page = request.args.get("page") or 1
    awal =  int(page)*10 - 10
    akhir = int(page)*10
    
    # Load your pickle file here
    anime = pickle.load(open("./movies_list.pkl", "rb"))
    try:
        d = json.loads(anime[awal:akhir].to_json(orient = 'records'))
        return GetDto.getDto(d, True), 200
    except:
        return GetDto.getDto([], False), 500
    # return jsonify({"data": json.loads(anime[awal:akhir].to_json(orient = 'records'))})

@app.route('/api/get/<name>')
def get_data_detail(name):
    
    # Load your pickle file here
    anime = pickle.load(open("./movies_list.pkl", "rb"))
    try:
        d = json.loads(anime[anime["Name"] == name].to_json(orient = 'records'))[0]
        return GetDto.getDto(d, True), 200
    except:
        return GetDto.getDto([], False), 500
    # return jsonify({"data": json.loads(anime[awal:akhir].to_json(orient = 'records'))})

@app.route("/api/anime")
async def detail():
    try:
        s = request.args.get('s')
        print(s)
        anime = await get_list_anime(s)
        return GetDto.getDto(anime, True), 200
    except:
        return GetDto.getDto([], False), 404
    
@app.route("/api/anime/stream")
async def stream():
    try:
        s = request.args.get('s')
        anime = await get_stream(s)
        print("ini", anime)
        return GetDto.getDto(anime, True), 200
    except Exception as e:
        print(e)
        return GetDto.getDto([], False), 404
    
@app.route("/api/anime/detail")
async def episode():
    try:
        s = request.args.get('s')
      
        eps = await get_episodes(s) 
       
        return GetDto.getDto(eps[::-1], True), 200
    except:
        return GetDto.getDto([], False), 404



@app.route("/api/top")
def get_top_anime():
    anime = pickle.load(open("./movies_list.pkl", "rb"))
    anime["Score"] = pd.to_numeric(anime["Score"],errors="coerce")
    idx = anime["Score"].sort_values(ascending=False).index
    d = json.loads(anime.iloc[idx][0:10].to_json(orient = 'records'))
   
    return GetDto.getDto(d, True), 200

@app.route("/api/recommend")
def get_recommend():
    s = request.args.get("s")
    rec = recommend(s)
    # print(rec.to_json(orient="records"))
    try:
        d = json.loads(rec.to_json(orient="records"))
        return GetDto.getDto(d, True), 200
    except:
        return GetDto.getDto([], False), 500
    # return jsonify({"data": json.loads(rec.to_json(orient="records"))})

    
async def get_stream(url):
    browser = await launch(handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
    page = await browser.newPage()
    try:
        await page.goto(url)
    
        await page.click("#play-asu")
        await page.waitForSelector('#select-mirror-container select#mirrorList')
        await page.select('select#mirrorList', 'v720p,krakenfiles')
         
        await page.waitForFunction('document.getElementById("iframedc").src != "about:blank"')
        
        
        search = await page.evaluate("""() => {
       
        let element = document.querySelector('iframe#iframedc');
        return element.src;
        
                                }
                                """)
       
 
      
       
    except Exception as e:
        print(e)
    finally:
        print("TERTUTUP")
        await browser.close()
    return search

async def get_episodes(s):
    browser = await launch(handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
    page = await browser.newPage()
    print("Ini", s)
    try:
        await page.goto(s)
       
       
 
        p =  await page.evaluate("""() => {
        let arr = [];
        let element = document.querySelectorAll('.lchx a');
        element.forEach((el)=>{
                                
            arr.push(el.href);                   
        });
        return arr;
        
                                }
                                """)
        # element = await page.querySelectorAll("span.lchx")
        # p = await page.evaluate("""(element) => element""", element)
        
        await page.screenshot({'path': 'screenshot.png'})

    except Exception as e:
        print(e)
    finally:
        print("TERTUTUP")
        await browser.close()
    return p 

async def get_list_anime(title):
    browser = await launch(handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
    page = await browser.newPage()
    try:
        await page.goto('https://tv1.kuronime.vip/')
        await page.type('.search-live', title)
        await page.click("#submit")
        await page.waitForNavigation()
        # element = await page.querySelector('div.bsx a')
        # title = await page.evaluate('(element) => element.href', element)
        search =  await page.evaluate("""() => {
        let arr = [];
        let element = document.querySelectorAll('div.bsx a');
    
        element.forEach((el, index)=>{
            let img = document.querySelectorAll('div.bsx div.limit img.lazyloaded')[index];
            let title = document.querySelectorAll('div.bsx div.tt h4')[index];
                            
            let temp = {title: title.textContent, link:el.href, img: img.src};
                                            
            arr.push(temp);                   
        });
        return arr;
        
                                }
                                """)    
       
    
    finally:
        print("TERTUTUP")
        await browser.close()
    return search


def recommend(title):
    result = pd.DataFrame(columns=['anime_id', 'Name', 'English name', 'Other name', 'Score', 'Genres', 
       'Synopsis', 'Type', 'Episodes', 'Aired', 'Premiered', 'Status',      
       'Producers', 'Licensors', 'Studios', 'Source', 'Duration', 'Rating', 
       'Rank', 'Popularity', 'Favorites', 'Scored By', 'Members', 'Image URL'])  # Buat DataFrame kosong
    
    try:
        anime = pickle.load(open("./movies_list.pkl", "rb"))
        similarity = pickle.load(open("./similarity.pkl", "rb"))
        idx = anime[anime["Name"].str.contains(title, case=False)].index[0]
        
        sm = sorted(enumerate(list(similarity[idx])), reverse=True, key=lambda vector: vector[1])
        
        # Mengisi DataFrame dengan hasil rekomendasi
        for i in sm[:5]:
            result.loc[len(result)] = anime.iloc[i[0]]
            # print(new_data.iloc[i[0]])
            # print(new_data.columns)
            # result = result.append(new_data.iloc[i[0]], ignore_index=True)
    except:
        pass
    # print("ini", result)
    return result



if __name__ == '__main__':
    app.run(debug=True)
 