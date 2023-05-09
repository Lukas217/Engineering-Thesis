import pyvisa
import time
import numpy as np
import csv

# Characteristic - 'agg' for not opening while generation
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

# Sending mail
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import time
import os

class Tektronix():

    # Connection
    def connect_to_oscilloscope(self):
     
        rm = pyvisa.ResourceManager()
       
        oscilloscope = rm.open_resource('TCPIP0::192.168.0.30::INSTR')
        wynik = 'Połączono z oscyloskopem'
        oscilloscope.timeout = 10000 
        return wynik, oscilloscope, rm
    
    # Info
    def info_from_oscilloscope(self, oscilloscope):
        oscilloscope_info = oscilloscope[1].query('*idn?')
        return oscilloscope_info

    # Reset
    def reset_oscilloscope(self, oscilloscope):
        oscilloscope_reset = oscilloscope[1].write('*rst')
        return oscilloscope_reset
    
    # Getting plot
    # from -> https://github.com/tektronix/Programmatic-Control-Examples
    def get_plot_from_oscilloscope(self, oscilloscope, which_channel, vertical_scale, horizontal_scale):
        try:
            #Clearing old measurements and deleting
            os.remove('/home/student/webserver/data/tektronix_oscilloscope.png')
            record = 0
        except:
            pass
        # Closing first channel because its always showing and reset
        oscilloscope[1].write(f'*rst') 
        oscilloscope[1].write(f'DISplay:GLObal:CH1:STATE 0') 
        # Choosing proper channel
        oscilloscope[1].write(f'DISplay:GLObal:CH{which_channel}:STATE 1') 
        t1 = time.perf_counter()

        # Opc returns 1 if all operations are completed
        r = oscilloscope[1].query('*opc?') # sync
        t2 = time.perf_counter()
        print('reset time: {}'.format(t2 - t1))

        # Changing data to lowercase - user can input everything
        vertical_scale.lower()
        horizontal_scale.lower()
        # Auto set
        if vertical_scale == 'auto' and horizontal_scale == 'auto':
            oscilloscope[1].write('autoset EXECUTE') # autoset jak przycisk
        # Settings by user
        else:
            oscilloscope[1].write(f'CH1:SCAle {vertical_scale}') # od 100V do 5mV
            oscilloscope[1].write(f'HORizontal:MODE:SCAle {horizontal_scale}') #1ks - 40 ps [s] ex. 2e-9'

        # Checking autoset time
        t3 = time.perf_counter()
        r = oscilloscope[1].query('*opc?')
        t4 = time.perf_counter()
        print('autoset time: {} s'.format(t4 - t3)) 

        # I/O config
        oscilloscope[1].write('header 0')
        oscilloscope[1].write('data:encdg SRIBINARY')
        oscilloscope[1].write(f'data:source CH{which_channel}')
        # First sample
        oscilloscope[1].write('data:start 1')
        record = int(oscilloscope[1].query('horizontal:recordlength?'))
        # Last sample
        oscilloscope[1].write('data:stop {}'.format(record))
        # 1 byte per sample
        oscilloscope[1].write('wfmoutpre:byt_n 1')

        # Acq config
        # Stop
        oscilloscope[1].write('acquire:state 0') 
        oscilloscope[1].write('acquire:stopafter SEQUENCE')
        # Run
        oscilloscope[1].write('acquire:state 1') 
        t5 = time.perf_counter()
        r = oscilloscope[1].query('*opc?') 
        t6 = time.perf_counter()
        print('acquire time: {} s'.format(t6 - t5))

        # Data query
        t7 = time.perf_counter()
        bin_wave = oscilloscope[1].query_binary_values('curve?', datatype='b', container=np.array)
        print(f'(test {bin_wave})')
        t8 = time.perf_counter()
        print('transfer time: {} s'.format(t8 - t7))

        # retrieve scaling factors
        tscale = float(oscilloscope[1].query('wfmoutpre:xincr?'))
        tstart = float(oscilloscope[1].query('wfmoutpre:xzero?'))
        vscale = float(oscilloscope[1].query('wfmoutpre:ymult?')) # volts / level
        voff = float(oscilloscope[1].query('wfmoutpre:yzero?')) # reference voltage
        vpos = float(oscilloscope[1].query('wfmoutpre:yoff?')) # reference position (level)

        # error checking
        r = int(oscilloscope[1].query('*esr?'))
        print('event status register: 0b{:08b}'.format(r))
        r = oscilloscope[1].query('allev?').strip()
        print('all event messages: {}'.format(r))

        oscilloscope[1].close()
        oscilloscope[2].close()

        # create scaled vectors
        # horizontal (time)
        total_time = tscale * record
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff

        # plotting
        plt.clf() # clearing old plot
        plt.plot(scaled_time, scaled_wave)
        plt.title(f'Kanał {which_channel}') # plot label
        plt.xlabel('Czas [s]') # x label
        plt.ylabel('Napięcie [V]') # y label
        plt.savefig(f'webserver/data/tektronix_oscilloscope.png')
    
    # Sending email with png
    def send_mail(self, user_mail):
        # Email Data
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587 
        EMAIL_USERNAME = 'your_email'
        EMAIL_PASSWORD = 'your_email_password' 

        # From, To, Date, Subject - of email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = user_mail
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Charakterysyka - Oscyloskop Tektronix MSO6'

        msg.attach(MIMEText('Wiadomosc wygenerowana automatycznie.\nW zalaczniku plik z pomiarami.'))

        # Sending characteristic nr.1
        with open('/home/student/webserver/data/tektronix_oscilloscope.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='tektronix_oscilloscope.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename=f'webserver/data/tektronix_oscilloscope.png')
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            msg.attach(mime)
        
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_USERNAME, user_mail, msg.as_string())
        smtp.quit()
        
    # Data logger
    # from -> https://github.com/tektronix/Programmatic-Control-Examples
    def data_logger(self, oscilloscope, seconds, which_channel):
        
        # Clearing old data
        try:
            #Clearing old measurements and deleting
            os.remove('/home/student/webserver/data/oscilloscope_data_logger.csv')
        except:
            pass
        # Data for first start
        results_one = []
        results_two = []
        results_three = []
        results_four = []
        results_five = []
        results_six = []
        results_seven = []
        results_eight = []
        results_nine = []
        results_ten = []
        results_eleven = []
        rows = []

        results_one.clear()
        results_two.clear()
        results_three.clear()
        results_four.clear()
        results_five.clear()
        results_six.clear()
        results_seven.clear()
        results_eight.clear()
        results_nine.clear()
        results_ten.clear()
        results_eleven.clear()
        rows.clear()
        

        # Making new list for data - could be sql here
        results_one = []
        results_two = []
        results_three = []
        results_four = []
        results_five = []
        results_six = []
        results_seven = []
        results_eight = []
        results_nine = []
        results_ten = []
        results_eleven = []
        rows = []

        # Preparing
        oscilloscope[1].write('*rst') # reset
        oscilloscope[1].query('*opc?') # sync
        oscilloscope[1].write(f'DISplay:GLObal:CH1:STATE 0') 

        # Settings - probably needed- scope.write('data:source CH1')
        oscilloscope[1].write(f'DISplay:GLObal:CH{which_channel}:STATE 1') 
        
        #Set up oscilloscope[1] - autoset
        oscilloscope[1].write('autoset EXECUTE') # autoset
        oscilloscope[1].query('*opc?') # sync

        oscilloscope[1].write('acquire:state 0') # stop
        oscilloscope[1].write('acquire:stopafter SEQUENCE') # single

        # Set up measurements
        one = oscilloscope[1].write("MEASUREMENT:ADDMEAS FREQUENCY") # 1 pomiar czestotliwosci
        two = oscilloscope[1].write("MEASUREMENT:ADDMEAS MAXImum") # 2 pomiar maximum data loger
        three = oscilloscope[1].write("MEASUREMENT:ADDMEAS MINImum") # 3 pomiar minimum data loger
        four = oscilloscope[1].write("MEASUREMENT:ADDMEAS ALLAcqs:PK2PK") # 4 pomiar peak to peak
        five =  oscilloscope[1].write("MEASUREMENT:ADDMEAS POVERSHOOT") # 5 positive overshot
        six = oscilloscope[1].write("MEASUREMENT:ADDMEAS NOVershoot") # 6 negative overshot
        seven = oscilloscope[1].write("MEASUREMENT:ADDMEAS MEAN") # 7 negative overshot
        eight = oscilloscope[1].write("MEASUREMENT:ADDMEAS RMS") # 8 RMS
        nine = oscilloscope[1].write("MEASUREMENT:ADDMEAS PERIOD") # 9 PERIOD
        ten = oscilloscope[1].write("MEASUREMENT:ADDMEAS PDUTY") # 10 positive duty cycle w %
        eleven = oscilloscope[1].write("MEASUREMENT:ADDMEAS NDUTY") # 11 negative duty cycle w %


        for x in range(seconds):

            #acquire
            oscilloscope[1].write('acquire:state 1') # run
            r = oscilloscope[1].query('*opc?') # sync

            #query measurement
            meas1 = float(oscilloscope[1].query("measu:meas1:resu:curr:mean?")) #1
            results_one.append(meas1)
            meas2 = float(oscilloscope[1].query("measu:meas2:resu:curr:mean?")) #2
            results_two.append(meas2)
            meas3 = float(oscilloscope[1].query("measu:meas3:resu:curr:mean?")) #3
            results_three.append(meas3)
            meas4 = float(oscilloscope[1].query("measu:meas4:resu:curr:mean?")) #4
            results_four.append(meas4)
            meas5 = float(oscilloscope[1].query("measu:meas5:resu:curr:mean?")) #5
            results_five.append(meas5)
            meas6 = float(oscilloscope[1].query("measu:meas6:resu:curr:mean?")) #6
            results_six.append(meas6)
            meas7 = float(oscilloscope[1].query("measu:meas7:resu:curr:mean?")) #7
            results_seven.append(meas7)
            meas8 = float(oscilloscope[1].query("measu:meas8:resu:curr:mean?")) #8
            results_eight.append(meas8)
            meas9 = float(oscilloscope[1].query("measu:meas9:resu:curr:mean?")) #9
            results_nine.append(meas9)
            meas10 = float(oscilloscope[1].query("measu:meas10:resu:curr:mean?")) #10
            results_ten.append(meas10)
            meas11 = float(oscilloscope[1].query("measu:meas11:resu:curr:mean?")) #11
            results_eleven.append(meas11)

            fieldnames = ['Czestotliwość', 'Największa', 'Najmniejsza', 'P2P',
                            'Dodatnie przekroczenie', 'Ujemne przekroczenie',
                             'Średnia', 'RMS', 'Okres', 'Dodatni cykl pracy',
                              'Ujemny cykl pracy']
            rows.append({f'{fieldnames[0]}':f'{meas1}', f'{fieldnames[1]}':f'{meas2}',
                        f'{fieldnames[2]}':f'{meas3}', f'{fieldnames[3]}':f'{meas4}',
                        f'{fieldnames[4]}':f'{meas5}', f'{fieldnames[5]}':f'{meas6}',
                        f'{fieldnames[6]}':f'{meas7}', f'{fieldnames[7]}':f'{meas8}',
                         f'{fieldnames[8]}':f'{meas9}', f'{fieldnames[9]}':f'{meas10}',
                         f'{fieldnames[10]}':f'{meas11}'})
        
            time.sleep(0.2)

        file_csv = open('webserver/data/oscilloscope_data_logger.csv', 'w', encoding='UTF8', newline='') 
        with file_csv:
            writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        #loop back to acquire n times
        oscilloscope[1].close()
        oscilloscope[2].close()     

        # Sending email with png
    def send_csv_mail(self, user_mail):
        # Email Data
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587 
        EMAIL_USERNAME = 'your_email'
        EMAIL_PASSWORD = 'your_email_password' 

        # From, To, Date, Subject - of email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = user_mail
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Plik z danymi pomiarowymi - Oscyloskop Tektronix MSO6'

        msg.attach(MIMEText('Wiadomosc wygenerowana automatycznie.\nW zalaczniku plik z pomiarami.'))

        # Sending characteristic nr.1
        with open('/home/student/webserver/data/oscilloscope_data_logger.csv', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='oscilloscope_data_logger.csv')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename=f'webserver/data/oscilloscope_data_logger.csv')
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            msg.attach(mime)
        
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_USERNAME, user_mail, msg.as_string())
        smtp.quit()

#source: https://github.com/tektronix/Programmatic-Control-Examples
#source: https://bc-robotics.com/tutorials/sending-email-using-python-raspberry-pi/