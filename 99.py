#a=int(input('请输入一条边'))
#b=int(input('请输入另一条边'))
#if a>0 and b>0:
    #c=(a*a+b*b)**0.5
    #print(f'斜边长是:{c:.2f}')
#else:
     #print("不能构成三角形")




#import requests
#url ="https://httpbin.org/get"
#payload ={
#"name":"张三",
#"age": 25,
#"city":"Beijing"
#}
#res = requests.get (url, params=payload)
#print("最终请求URL:", res. url)
#print("响应内容：",res.json())


#import requests
#resp=requests.get('https://httpbin.org/get')
#print("类型(text):",type(resp.text))
#data=resp.json()
#print("类型(json):",type(data))


#import requests
#resp = requests.get('http://httpbin.org/status/404')
#print("状态码:",resp.status_code)
#try:
    #resp.raise_for_status()
#except requests.HTTPError as e:
    #print("请求出错:",e)


#import requests
#try:
    #r=requests.get('https://httpbin.org/delay/2',timeout=1)
    #r.raise_for_statue()
    #print("请求成功!")
#except requests.exceptions.Timeout:
    #print("请求超时,请检查网络或重试")
#except requests.exception.RequestException as e:
    #print("未知错误:",e)

#import requests

#def f():
    #try:
        #a= requests.get("http://httpbin.org/ip", timeout=5)
        #if a.status_code == 200:
            #ip = a.json().get('origin')
            #print(f"IP 地址是：{ip}")
        #else:
            #print("请求失败")
   # except Exception as e:
        #print(f"出错：{e}")

#f()

import requests
print("1:查询某个当天的天气")
print("2:预测某个后四天的天气")
o=input("请输入1或2")
if o=='1':
    city = input("输入城市名称")
    a = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": city,
        "key": "48deb74ad53350cc6bbfac6dcf607a95",
        "extensions": "base",
        "output": "json"
    }

    try:
        res_base = requests.get(a, params=params, timeout=10)
        data_base = res_base.json()

        if data_base["status"] == "1":
            if data_base["lives"]:
                weather = data_base["lives"][0]
                print(f"城市: {weather['city']}")
                print(f"天气: {weather['weather']}")
                print(f"温度: {weather['temperature']}℃")
                print(f"风向: {weather['winddirection']}")
                print(f"风力: {weather['windpower']}级")
                print(f"更新时间: {weather['reporttime']}")
            else:
                print("无法查询到当前城市")
        else:
            print(f"查询失败：{data_base['info']}")

    except Exception as e:
        print(f"请求出错：{e}")

elif o=='2':

    city = input("输入城市名称")
    a = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": city,
        "key": "48deb74ad53350cc6bbfac6dcf607a95",
        "extensions": "all",
        "output": "json"
    }

    try:
        res_all = requests.get(a, params=params, timeout=10)
        data_all = res_all.json()
        if data_all["status"] == "1":
            if data_all["forecasts"]:
                print("该城市未来4天的天气预报")
                forecasts=data_all["forecasts"][0]
                for cast in forecasts["casts"]:
                    print(f"日期: {cast['date']} 星期{cast['week']}")
                    print(f"白天: {cast['dayweather']} {cast['daytemp']}℃ {cast['daywind']} {cast['daypower']}级")
                    print(f"夜间: {cast['nightweather']} {cast['nighttemp']}℃ {cast['nightwind']} {cast['nightpower']}级")
                    print("-" * 20)
        else:
            print(f"查询失败：{data_all['info']}")

    except Exception as e:
        print(f"请求出错：{e}")
else:
    print("请输入1或者2")