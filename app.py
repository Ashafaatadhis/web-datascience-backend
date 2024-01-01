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

@app.route("/api/anime")
async def episode():
    s = request.args.get('s')
    print(s)
    anime = await get_episodes(s)
    return GetDto.getDto(anime, True), 200

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


# def scrap():
#     BeautifulSoup.
    
 
    
async def get_episodes(title):
    browser = await launch(handleSIGINT=False,handleSIGTERM=False,handleSIGHUP=False)
    page = await browser.newPage()
    await page.goto('https://tv1.kuronime.vip/')
    await page.type('.search-live', title)
    await page.click("#submit")
    await page.waitForNavigation()
    # element = await page.querySelector('div.bsx a')
    # title = await page.evaluate('(element) => element.href', element)
    search =  await page.evaluate("""() => {
    let arr = [];
    let element = document.querySelectorAll('div.bsx a');
    element.forEach((el)=>{
                             
        arr.push(el.href);                   
    });
    return arr;
    
                             }
                             """)
    
    await page.goto(search[-1])
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
    await browser.close()
    return p


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
 