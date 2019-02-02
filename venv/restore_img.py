import sqlite3
import os
import shutil

if not os.access('./image', os.R_OK):
 os.mkdir('image')
else:
 shutil.rmtree('image')
 os.mkdir('image')

conn = sqlite3.connect('rozetka.db')
c = conn.cursor()
c1 = conn.cursor()
sql = 'select Image, Image_name from cellphones'

num = c.execute(sql)

for i in num:
    img_data, img_name = c.fetchone()

#    print(img_data)
    with open(img_name,'wb') as img_out:
        img_out.write(img_data)
        img_out.close()



c.close()
conn.close()
