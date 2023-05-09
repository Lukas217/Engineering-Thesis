# Characteristic - 'agg' for not opening while generation
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

import pyvisa, time, csv

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



class MostekRLC:
    
    # Global data
    global rlc_bridge
    global output_induc
    global output_resis
    global rows
    global freq_full, freq_medium, freq_short
 
    # Frequency input list

    # Full freq measurement
    freq_full = [20, 24, 25, 30, 36, 40, 45, 50, 60, 72, 75,
                90, 100, 120, 150, 180, 200, 240, 250, 300, 360, 400,
                450, 500,600, 720, 750, 800, 900, 1000, 1200, 1500,
                1800, 2000, 2400, 2500, 3000, 3600, 4000, 4500, 5000,
                6000, 7200, 7500, 8000, 9000, 10000, 12000, 15000,
                18000, 20000, 24000, 25000, 30000, 36000, 40000,
                45000, 50000, 60000, 72000, 75000, 80000, 90000,
                100000, 120000, 150000, 180000, 200000]

    # Medium freq measurement
    freq_medium = [20, 25, 36, 45, 60, 75, 100, 150, 200, 250, 360,
                    450, 600, 750, 900, 1200, 1800, 2400, 3000, 4000,
                    5000, 7200, 8000, 10000, 15000, 20000, 25000, 36000,
                     45000, 60000, 75000, 90000, 120000, 180000]  
    
    # Short freq measurement
    freq_short= [20, 60, 200, 600, 1800, 5000, 15000, 90000, 120000, 180000] 


    # Output list

    output_induc = []
    output_resis = []
    rows = []

    # Connection
    def rlc_connect(self):
    # Search for rlc device
        try:
            rm = pyvisa.ResourceManager()
            a = rm.list_resources()
            print(a)
            # Connecting with rlc (read_termination is selected because of timeout error)
            for i in a:
                
                # Checking if rlc is connected to usb
                if i[0:15] == 'ASRL/dev/ttyUSB':
                    rlc_bridge = rm.open_resource(i, read_termination='\r')
                    print(rlc_bridge)
                    return rlc_bridge
        except:
            pass
    
    # Information about device
    def rlc_info(self, rlc_bridge):
        # RLC info data
        try:
            rlc_info_data = rlc_bridge.query('*IDN?')
            print(f'rlc_bri: {rlc_info_data}')
            return rlc_info_data
        except:
            return 'Nie połączono z urzadzeniem'
    
    # Selecting measurement functions
    def witch_program(self, rlc_bridge, number_of_prg):
        # # Selecting measurement functions
        try:
            rlc_bridge.write(f'CALL 1')
            rlc_bridge.write(f'PMOD{number_of_prg}')
        except:
            pass

    # Selecting measurement speed
    def measurement_speed(self, rlc_bridge,witch_speed):
        rlc_bridge.write(f'RATE{witch_speed}')
    
    # Selecting frequency range
    def frequency_range(self, witch_freq_range):
        return witch_freq_range

    # Make measurement
    def make_measurement(self, rlc_bridge, witch_freq_range, interval_between_samples):

        try:
            #Clearing old measurements and deleting
            os.remove('/home/student/webserver/data/rlc_data.csv')
            #Clearing old plots
            os.remove('/home/student/webserver/data/characteristic.png')
            os.remove('/home/student/webserver/data/characteristic_nr2.png')
        except:
            pass
        output_induc.clear()
        output_resis.clear()
        rows.clear()

        # User input - with freq range?
        if witch_freq_range == '0':
            freq_range = freq_full
        elif witch_freq_range == '1':
            freq_range = freq_medium
        else:
            freq_range = freq_short

        #Creating new csv for measurement
        with open('webserver/data/rlc_data.csv', 'w', encoding='UTF8', newline='') :
            pass
        
       
        # Loop
        for i in freq_range:
            try:
                rlc_bridge.write(f'FREQ{i}')
                time.sleep(float(interval_between_samples))
                # Inductance resut
                induc_query = rlc_bridge.query('XMAJ?')
                
                induc = float(induc_query)
                result_induc = f'{induc}'

                if induc_query == '0':
                    time.sleep(2)
                    induc_query = rlc_bridge.query('XMAJ?')
                    induc = float(induc_query)
                    result_induc = f'{induc}'

                # Resistance result
                resis = float(rlc_bridge.query('XMIN?'))
        
                # result_resis = f'{Float(resis):.3h}H'
                result_resis = f'{resis}'

                # Adding to list 0:6 to delete unit at the end
                output_induc.append(result_induc)
                # output_resis.append(result_resis[0:6])
                output_resis.append(result_resis)
                # Title of columns in csv
                with_program = rlc_bridge.query(f'PMOD?')

                #L-Q
                if with_program == '1':
                    fieldnames = ['Czestotliwosc', 'Indukcyjnosc', 'Dobroc']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #L-R
                elif with_program == '2':
                    fieldnames = ['Czestotliwosc', 'Indukcyjnosc', 'Rezystancja']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #C-D
                elif with_program == '3':
                    fieldnames = ['Czestotliwosc', 'Pojemnosc', 'Wspolczynnik rozpraszania']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #C-R
                elif with_program == '4':
                    fieldnames = ['Czestotliwosc', 'Pojemnosc', 'Rezystancja']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #R-Q
                elif with_program == '5':
                    fieldnames = ['Czestotliwosc', 'Rezystancja', 'Dobroc']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #Z-θ
                elif with_program == '6':
                    fieldnames = ['Czestotliwosc', 'Impedancja pozorna', 'Kat fazowy']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #Y-θ
                elif with_program == '7':
                    fieldnames = ['Czestotliwosc', 'Admitancja', 'Kat fazowy']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #R-X
                elif with_program == '8':
                    fieldnames = ['Czestotliwosc', 'Rezystancja', 'Reaktancja']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #G-B
                elif with_program == '9':
                    fieldnames = ['Czestotliwosc', 'Konduktacja', 'Susceptancja']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #N-θ
                elif with_program == '10':
                    fieldnames = ['Czestotliwosc', 'Przekładnia transformatorowa', 'Roznica faz']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)
                #M
                elif with_program == '11':
                    fieldnames = ['Czestotliwosc', 'Indukcyjnosc wzajemna transformatora']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}'},)
                else:
                    fieldnames = ['Tryb auto', 'Tryb Auto', 'Tryb Auto']
                    rows.append({f'{fieldnames[0]}':f'{i}', f'{fieldnames[1]}':f'{result_induc}', f'{fieldnames[2]}':f'{result_resis[0:6]}'},)

            except:
                    return 'Źle wprowadzona konfiguracja. \n Wprowadz poprawnie!'

        #Setting first frequency after all measurements
        rlc_bridge.write(f'FREQ{20}')
        
    # Csv generating      
    def make_csv(self, rlc_bridge):
        # Title of columns in csv
        try:
            with_program = rlc_bridge.query(f'PMOD?')
        
            #L-Q
            if with_program == '1':
                fieldnames = ['Czestotliwosc', 'Indukcyjnosc', 'Dobroc']
            #L-R
            elif with_program == '2':
                fieldnames = ['Czestotliwosc', 'Indukcyjnosc', 'Rezystancja']
            #C-D
            elif with_program == '3':
                fieldnames = ['Czestotliwosc', 'Pojemnosc', 'Wspolczynnik rozpraszania']
            #C-R
            elif with_program == '4':
                fieldnames = ['Czestotliwosc', 'Pojemnosc', 'Rezystancja']
            #R-Q
            elif with_program == '5':
                fieldnames = ['Czestotliwosc', 'Rezystancja', 'Dobroc']
            #Z-θ
            elif with_program == '6':
                fieldnames = ['Czestotliwosc', 'Impedancja pozorna', 'Kat fazowy']
            #Y-θ
            elif with_program == '7':
                fieldnames = ['Czestotliwosc', 'Admitancja', 'Kat fazowy']
            #R-X
            elif with_program == '8':
                fieldnames = ['Czestotliwosc', 'Rezystancja', 'Reaktancja']
            #G-B
            elif with_program == '9':
                fieldnames = ['Czestotliwosc', 'Konduktacja', 'Susceptancja']
            #N-θ
            elif with_program == '10':
                fieldnames = ['Czestotliwosc', 'Przekladnia transformatorowa', 'Roznica faz']
            #M
            elif with_program == '11':
                fieldnames = ['Czestotliwosc', 'Indukcyjność wzajemna transformatora']
            else:
                fieldnames = ['Tryb auto', 'Tryb Auto', 'Tryb Auto']


            file_csv = open('webserver/data/rlc_data.csv', 'w', encoding='UTF8', newline='') 
            with file_csv:
                writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        except:
            pass

    # Sending email
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
        msg['Subject'] = 'Dane pomiarowe - Mostek RLC HM8118 RHODE&SCHWARZ'

        msg.attach(MIMEText('Wiadomosc wygenerowana automatycznie.\nW zalaczniku pliki utworzone podczas pomiarów.'))

        
        part = MIMEBase('application', "octet-stream")
        with open('/home/student/webserver/data/rlc_data.csv', 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path('/home/student/webserver/data/rlc_data.csv').name))

        msg.attach(part)

        # Sending characteristic nr.1
        with open('/home/student/webserver/data/characteristic.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='haracteristic.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='characteristic.png')
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            msg.attach(mime)

        # Sending characteristic nr.2
        with open('/home/student/webserver/data/characteristic_nr2.png', 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='characteristic_nr2.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='characteristic_nr2.png')
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
    
    # Circuit type 1- auto, 2- ser, 3 -par
    def circuit_type(self,rlc_bridge, circ_type):
        rlc_bridge.write(f'CIRC{circ_type}')
        
    # Circuit range + resistance
    def circuit_range(self,rlc_bridge, circ_range):
        if circ_range == '0':
            rlc_bridge.write(f'RNGH{circ_range}')
        else:
            rlc_bridge.write(f'RNGH{1}')
            rlc_bridge.write(f'RNGE{circ_range}')
    
    # Voltage for measurement
    def voltage(self,rlc_bridge, voltage):
        print(voltage)
        rlc_bridge.write(f'VOLT{voltage}')
    
    # DC bias
    def dc_bias(self, rlc_bridge, dc_bias_choice, dc_bias_volt, dc_bias_curr, program_number):
        # Reset
        time.sleep(1)
        # If dc bias is set to nothing or internal
        if dc_bias_choice == '0':
            rlc_bridge.write(f'CONV0')
            rlc_bridge.write(f'BIAS0')
        
        # Internal without conv
        if dc_bias_choice == '1' and (program_number == '3' or program_number == '4' or program_number == '6' or program_number == '8'):
            rlc_bridge.write(f'CONV0')
            rlc_bridge.write(f'BIAS1')
            rlc_bridge.write(f'VBIA{dc_bias_volt}')

        # Internal with conv - current
        if dc_bias_choice == '1' and (program_number == '1' or program_number == '2' or program_number == '10' or program_number == '11'):
            rlc_bridge.write(f'CONV1')
            rlc_bridge.write(f'BIAS1')
            rlc_bridge.write(f'IBIA{dc_bias_curr}')

        # External with conv - current
        if dc_bias_choice == '2' and (program_number == '1' or program_number == '2' or program_number == '10' or program_number == '11'):
            rlc_bridge.write(f'CONV1')
            rlc_bridge.write(f'BIAS2')
            rlc_bridge.write(f'IBIA{dc_bias_curr}')

        if dc_bias_choice == '2' and (program_number == '3' or program_number == '4' or program_number == '6' or program_number == '8'):
            rlc_bridge.write(f'CONV1')
            rlc_bridge.write(f'BIAS2')
            rlc_bridge.write(f'VBIA{dc_bias_volt}')
        
    # Compensation
    def compensation(self, rlc_bridge, compensation):
        
        # Full speed
        rlc_bridge.write('RATE1')

        # Return 1 if all tasks are done
        rlc_ready = rlc_bridge.query('*OPC?')
        
        # Before compens
        rlc_bridge.write(f'CALL 1')

        # User selected open compensation
        if compensation == '1' and rlc_ready == '1':
            compensation_write = 'CROP'
        # User selecter short compensation
        if compensation == '2' and rlc_ready == '1' :
            compensation_write = 'CRSH'

        # Result
        result = rlc_bridge.write(compensation_write)


        if result == '-1':
            try:
                result = rlc_bridge.write(compensation_write)
            except:
                return 'Error'

      
    
    # Reset
    def reset(self, rlc_bridge):
        rlc_bridge.write(f'*RST')

    # Make plot 1st data
    def plot_char(self, frequency_range, rlc_bridge):
      
        # Plot
        # This loop is for converting output type for plot
        output_induc_to_float = []
        for output in output_induc:
            output_induc_to_float.append(float(output))
        y=output_induc_to_float

        if frequency_range == '2':
            x = freq_short
        if frequency_range == '1':
            x = freq_medium
        if frequency_range == '0':
            x = freq_full

        fig, ax = plt.subplots(figsize=(10,8), dpi=200)
        # aprox = np.polyfit(x,y,1)
        # poly1d = np.poly1d(aprox) 
        
        # ax.plot(x, y, 'ro', x, poly1d(x), '--b')
        ax.set_ylim(ymin=0)
        ax.set_ylim(ymax=(max(output_induc_to_float)+ min(output_induc_to_float)))
        ax.plot(x, y, 'ro')
        #ax.set_title('Charakterystyka', fontsize=20)
        with_program = rlc_bridge.query(f'PMOD?')
        
        #L
        if with_program == '1' or with_program == '2':
            ax.set_ylabel('L [H]', fontsize=15)
        #C
        elif with_program == '3' or with_program == '4':
            ax.set_ylabel('C [F]', fontsize=15)
        #R
        elif with_program == '5' or with_program == '8':
            ax.set_ylabel('R [Ω]', fontsize=15)
        #Z
        elif with_program == '6':
            ax.set_ylabel('Z [Ω]', fontsize=15)
        #Y
        elif with_program == '7':
            ax.set_ylabel('Y [S]', fontsize=15)
        #G
        elif with_program == '9':
            ax.set_ylabel('G [S]', fontsize=15)
        #N
        elif with_program == '10':
            ax.set_ylabel('N [S]', fontsize=15)
        #M
        elif with_program == '11':
            ax.set_ylabel('M [H]', fontsize=15)
 
        ax.set_xlabel('f [Hz]', fontsize=15)
        ax.set_xscale('log')
        ax.grid()
        fig.savefig('webserver/data/characteristic.png')

    # Make plot 2st data
    def plot_charv2(self, frequency_range, rlc_bridge):
      
        # Plot
        # This loop is for converting output type for plot
        output_resis_to_float = []
        for output in output_resis:
            output_resis_to_float.append(float(output))
        y=output_resis_to_float

        if frequency_range == '2':
            x = freq_short
        if frequency_range == '1':
            x = freq_medium
        if frequency_range == '0':
            x = freq_full

        fig, ax = plt.subplots(figsize=(10,8), dpi=200)
        # aprox = np.polyfit(x,y,1)
        # poly1d = np.poly1d(aprox) 
        
        # ax.plot(x, y, 'ro', x, poly1d(x), '--b')
        ax.set_ylim(ymin=0)
        ax.set_ylim(ymax=(max(output_resis_to_float)+ min(output_resis_to_float)))
        ax.plot(x, y, 'ro')
        #ax.set_title('Charakterystyka')
        with_program = rlc_bridge.query(f'PMOD?')
        
        #Q
        if with_program == '1' or with_program == '5':
            ax.set_ylabel('Q', fontsize=15)
        #R
        elif with_program == '2' or with_program == '4':
            ax.set_ylabel('R [Ω]', fontsize=15)
        #D
        elif with_program == '3':
            ax.set_ylabel('D', fontsize=15)
        #θ
        elif with_program == '6' or with_program == '7' or with_program == '10':
            ax.set_ylabel('θ [°]', fontsize=15)
        #X
        elif with_program == '8':
            ax.set_ylabel('X [Ω]', fontsize=15)
        #B
        elif with_program == '9':
            ax.set_ylabel('B [S]', fontsize=15)
        #M
        elif with_program == '11':
            return 
 
        ax.set_xlabel('f [Hz]', fontsize=15)
        ax.set_xscale('log')
        ax.grid()
        fig.savefig('webserver/data/characteristic_nr2.png')

#source: https://bc-robotics.com/tutorials/sending-email-using-python-raspberry-pi/