
from email.mime import text
from ds_sens_temp import ds_temp
from actual_date_time import actual_date_time
import time
import os

txt=[]
def temperature_measurements(how_many_temp_sens_data, how_many_temp_sec):
    # print(type(how_many_temp_sec))
    # print(type(how_many_temp_sens_data))
    txt.clear()
    for _ in range(0,how_many_temp_sens_data):
                first = f'{ds_temp()}\t {actual_date_time()[2]} \n'
                txt.append(first)
                # -1 because program is taking 1 more sec than in variable from user
                time.sleep(how_many_temp_sec-1)


    # os.chdir('/home/student/test')

    with open(r'webserver/data/temp_sens_data.txt', 'w') as fp:
        for item in txt:
            # write each item on a new line
            fp.write(item)
   
    return txt