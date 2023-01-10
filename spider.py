import requests
from bs4 import BeautifulSoup
import json
import traceback
import csv
headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
}

csv_obj = open('rentData.csv','w',encoding='utf-8', newline='')
csv.writer(csv_obj).writerow(['房屋编号','室','厅','卫','起始所在楼层','所跨楼层','总楼层','租金/月','面积/坪','管理费/月','周边学校','周边交通','周边医疗','购物中心','嫌惡設施'])
n = 1
success = 0
fail = 0
# 通用请求函数
def requests_houses(url):
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None

def main(page):
    #获取第page页的数据
    housesPageInfo = json.loads(requests_houses("https://rent.houseprice.tw/ws/list/?p=" + str(page)))
    housesList = housesPageInfo.get('webRentCaseGroupingList')

    for item in housesList:
        item_url =  'https://rent.houseprice.tw/ws/detail/'+ str(item.get('sid'))
        print('正在爬取' + item_url + '的数据...')
        try:
            # 获取房型信息接口的数据
            data = json.loads(requests_houses(item_url))
            # 房屋编号
            item_roomId = data.get('webRentCaseGroupingDetail').get('sid')
            # 室
            item_room = data.get('webRentCaseGroupingDetail').get('rm')
            if item_room == None or item_room == '' :
                item_room = 0
            # 厅
            item_livingRm = data.get('webRentCaseGroupingDetail').get('livingRm')
            if item_livingRm == None or item_livingRm == '' :
                item_livingRm = 0
            # 卫
            item_bathRm = data.get('webRentCaseGroupingDetail').get('bathRm')
            if item_bathRm == None or item_bathRm == '' :
                item_bathRm = 0
            # 起始所在楼层
            item_beginFloor = data.get('webRentCaseGroupingDetail').get('fromFloor')
            if item_beginFloor == '--' or item_beginFloor == '' or item_beginFloor == None:
                item_beginFloor = 0
                item_floor = 0
            else:
                # 所跨楼层
                item_floor = int(data.get('webRentCaseGroupingDetail').get('toFloor')) - int(data.get('webRentCaseGroupingDetail').get('fromFloor')) + 1
            # 总楼层
            item_upFloor = data.get('webRentCaseGroupingDetail').get('upFloor')
            # 租金
            item_price = data.get('webRentCaseGroupingDetail').get('rentPrice')
            # 坪
            item_buildPin = data.get('webRentCaseGroupingDetail').get('buildPin')
            # 管理费
            item_managementFee = str(data.get('webRentCaseGroupingDetail').get('managementFee'))
            if item_managementFee == '無' or item_managementFee == None or item_managementFee == '':
                item_managementFee = 0
            else:
                item_managementFee = int(item_managementFee[:-3].replace(',',''))
            # 统计周围建筑
            item_poiList = data.get('poi').get('poiList')
            transport = 0
            school = 0
            medic = 0
            shop = 0
            bad = 0
            for i in item_poiList:
                if i.get('categoryType') == 2:
                    school = school + 1
                elif i.get('categoryType') == 3:
                    medic = medic + 1
                elif i.get('categoryType') == 4:
                    shop = shop + 1
                elif i.get('categoryType') == 5:
                    bad = bad + 1
                elif i.get('categoryType') == 1:
                    transport = transport + 1
            # 写入csv
            global n
            csv.writer(csv_obj).writerow([item_roomId,item_room,item_livingRm,item_bathRm,item_beginFloor,item_floor,item_upFloor,item_price,item_buildPin,item_managementFee,school,transport,medic,shop,bad])
            n = n + 1
        except Exception as e:
            print(item_url + '数据处理失败:')
            traceback.print_exc()
            global fail
            fail = fail + 1
        else:
            print(item_url + '数据处理成功')
            global success
            success = success + 1


if __name__ == '__main__':
    for i in range(1, 2):
        main(i)
    print("爬虫执行完毕，成功" + str(success) + '条，失败' + str(fail) + '条')
    
csv_obj.close()