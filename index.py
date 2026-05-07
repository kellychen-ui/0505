from flask import Flask, request
import requests
import json

app = Flask(__name__)

CWA_API_KEY = "CWA-00042A92-71A6-4BE3-AC82-FE9E88ED9B62"

@app.route('/')
def home():
    return """
    <ul>
        <li><a href="/road">1. 台中市十大肇事路口</a></li>
        <li><a href="/weather">2. 天氣查詢</a></li>
    </ul>
    """

@app.route('/road')
def road():
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        json_data = json.loads(response.text)
        
        sorted_data = sorted(json_data, key=lambda x: int(x.get("總件數", 0)), reverse=True)
        top_10 = sorted_data[:10]
        
        result = "<h2>台中市十大肇事路口</h2><ul>"
        for item in top_10:
            result += f"<li>{item['路口名稱']}：發生 {item['總件數']} 件，主因是 {item['主要肇因']}</li>"
        result += "</ul><br><a href='/'>返回首頁</a>"
        
        return result
    except Exception as e:
        return f"讀取資料發生錯誤：{str(e)}<br><a href='/'>返回首頁</a>"

@app.route('/weather')
def weather():

    city = request.args.get('city')
    
    if not city:
        return """
        <h2>天氣查詢</h2>
        <form action="/weather" method="GET">
            <label for="city">請輸入欲查詢的縣市：</label>
            <input type="text" id="city" name="city" required>
            <button type="submit">查詢</button>
        </form>
        <br>
        <a href="/">返回首頁</a>
        """

    city = city.replace("台", "臺")
    # ---------------------------------

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWA_API_KEY}&locationName={city}"
    
    try:
        response = requests.get(url, verify=False)
        data = json.loads(response.text)
        
        if 'records' not in data or not data['records']['location']:
            return f"找不到「{city}」的天氣資料，請確認名稱是否輸入正確。<br><br><a href='/weather'>重新查詢</a> | <a href='/'>返回首頁</a>"
            
        location_data = data['records']['location'][0]
        weather_elements = location_data['weatherElement']
        wx = ""
        pop = ""
        for element in weather_elements:
            if element['elementName'] == 'Wx':
                wx = element['time'][0]['parameter']['parameterName']
            elif element['elementName'] == 'PoP':
                pop = element['time'][0]['parameter']['parameterName']
                
        return f"<h2>{city} 目前天氣</h2><p>天氣狀況：{wx}</p><p>降雨機率：{pop}%</p><br><a href='/weather'>重新查詢</a> | <a href='/'>返回首頁</a>"
        
    except Exception as e:
        return f"發生錯誤：{str(e)}。<br><a href='/weather'>重新查詢</a>"

if __name__ == '__main__':
    app.run(debug=True)
