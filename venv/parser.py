import bs4
import urllib.request as urllib
import ssl
import openpyxl
import sqlite3
import os
import shutil
import sys


url = "https://rozetka.com.ua/mobile-phones/c80003/preset=smartfon/" # url from where parsing
print(sys.argv[1])
# checking if directory image exist or not
if not os.access('./image', os.R_OK):
 os.mkdir('image')
else:
 shutil.rmtree('image')
 os.mkdir('image')

connect = sqlite3.connect('rozetka.db')
c = connect.cursor()
c.execute("drop table if exists cellphones") # delete table if exist
c.execute("create table if not exists cellphones"
          "(Title text,"
          "Description text,"
          "Price integer, "
          "Status text, "
          "Image blob, "
          "Image_name text)")

sql_insert  = "insert into cellphones (Title, Description, Price, Image_name, Status, Image) " \
              "values (?, ?, ?, ?, ?, ?) " # insert data of one item

#url = "https://bt.rozetka.com.ua/washing_machines/c80124/filter/"
# parsing url
context = ssl._create_unverified_context()
page = urllib.urlopen(url, context=context)
page_soup = bs4.BeautifulSoup(page,"html.parser")
price_script = page_soup.find_all('div','g-i-tile-i-box')
tmp = price_script
wb = openpyxl.Workbook()
ws = wb.create_sheet('Cellphones')
#preparing  xlsx file
title_tab = ['Title','Description','Price']
for i in range(1,len(title_tab) + 1):
 ws.cell(1,i).value = title_tab[i-1]

ws.column_dimensions['A'].width = 100
ws.column_dimensions['B'].width = 400
# parsing price, name of item and description of item
for i in range(len(tmp)):
 price = tmp[i].find('script').text.strip()
 price = price.replace('%22','"')
 price = price.replace('%7B','{')
 price = price.replace('%3A',':')
 price = price.replace('%2C',',')
 start = price.find('price":')
 stop = price.find(',"status"')
 start_status = price.find('sell_status":"')
 stop_status = price.find('","pl_bonus_charge_pcs')
 status = price[start_status+14:stop_status]
 title = tmp[i].find('div','g-i-tile-i-title clearfix').text.strip()
 # if description not exist then None
 try:
  descr = tmp[i].find('div','short-description','description').text
 except AttributeError:
  descr = 'None'
 # if status not exist then set Unknow status
 if len(status) > 15: status = 'Unknow'
 price = price[start+7:stop]
 # if price not exist then set price to 0
 if not price.isdigit(): price =0
 # put data to xls cells
 ws.cell(i+2,1).value = title
 ws.cell(i + 2, 2).value = descr
 ws.cell(i + 2, 3).value = price
 # parsing and download image
 img = tmp[i].find('a', 'responsive-img centering-child-img').img.attrs['src']
 img = img.replace('https', 'http')
 # context = ssl._create_default_https_context()
 file_name = img.split('/')
 urllib.urlretrieve(img, './image/' + file_name[5])
 data = (title, descr, price,'./image/' + file_name[5],status)
 file_path = './image/' + file_name[5]
 # reading image file like bytes for database storing
 with open(file_path,'rb') as img_byte:
  img_blob = img_byte.read()
  # preparing data (name of item, description of item, price, name of image file,
  # status avaliable of item and image) for storing to database
 data = (title, descr, price, './image/' + file_name[5], status, img_blob)
 c.execute(sql_insert, data)
 connect.commit()
 img_byte.close()

# storing price, name of item and description of item to xls file
wb.save('rozetka.xlsx')
wb.close()
connect.commit()
connect.close()