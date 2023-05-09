# Libraries
from flask import Flask, render_template,Response, redirect, send_file, session
# Sending mail
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

# My python files
from cpu_temp import temperature_of_raspberry_pi
from actual_date_time import actual_date_time
from delta_sm1500 import PSDelta
from ds_sens_temp import ds_temp
from led_control import led_control_on, led_control_off
import sens_temp
from forms import (DownloadForm, PSCheck, PSSettings, RlcForm, SearchForm,
                    TempForm, TempFormSendMail, DownloadForm, CompensationForm,
                    PSReset, ResetForm, ConnectionForm, MakeMeasurementForm, 
                    DownloadCharacteristicForm, DownloadCharacteristicv2Form,
                    OSCConnect, OSCReset, OSCCHAR, OSCCHARDownload, OSCDataLogger, OSCDataLoggerDownload)
from thermocouple import thermocouple_temp
from rlc_test import MostekRLC
from tektronix import Tektronix


app = Flask(__name__)


# 404 page not found handler
@app.errorhandler(404)
def not_found(e):
  return render_template('error_404.html')

# Home page
@app.route('/')
def home_page():
    template_data = {
        'cpu_temp' : f'',
        'date': f''
        }   
    return render_template('home.html', **template_data)

#############################################################################################

                                ### AUTOMATION PAGE ###

#############################################################################################

# Declaring my libraries for measurement equipment
bridge_class = MostekRLC()
power_supply_class = PSDelta()
oscilloscope_class = Tektronix()

# Home automation page
@app.route('/home_automation')
def home_automation():
    print(len(ps_device_info_data))

    # Clearing last data index from power supply temporary data
    if ps_device_connect_data[0] != 'Nie połączono':
        ps_device_connect_data[0] = 'Nie połączono'

    if ps_device_info_data[0] != '':
        ps_device_info_data[0] = ''
    
    if ps_device_temp_data[0] != '':
        ps_device_temp_data[0] = ''

    

    template_data = {
        'cpu_temp' : f'Temperatura CPU: {temperature_of_raspberry_pi()}',
        'date': f'Data: {actual_date_time()[1]}',
        'time': f'Czas: {actual_date_time()[0]}'
        }   
    return render_template('home_automation.html', **template_data)

# Information page with pdf and links
@app.route('/informations')
def informations():

    template_data = {
        }   
    return render_template('informations.html', **template_data)

# PDF for rlc
@app.route('/informations/rlc')
def informations_rlc():

    try:    
        path = "/home/student/webserver/informations/rlc_hm8118.pdf"
        return send_file(path)
        
    except TypeError:
        return informations() 

# PDF for power supply
@app.route('/informations/ps_delta')
def informations_ps_delta():

    try:    
        path = "/home/student/webserver/informations/zasilacz_delta_sm1500.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF for power supply - programming
@app.route('/informations/ps_delta_programming')
def informations_ps_delta_programming():

    try:    
        path = "/home/student/webserver/informations/zasilacz_programowanie.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF for power supply - ethernet config
@app.route('/informations/ps_delta_ethernet')
def informations_ps_delta_ethernet():
    try:    
        path = "/home/student/webserver/informations/konfiguracja_ethernet.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF for oscilloscope - manual
@app.route('/informations/oscilloscope_manual')
def informations_oscilloscope_manual():
    try:    
        path = "/home/student/webserver/informations/tektronix_mso6_instrukcja.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF for oscilloscope - programming
@app.route('/informations/oscilloscope_programming_manual')
def informations_oscilloscope_programming():
    try:    
        path = "/home/student/webserver/informations/tektronix_mso6_programming_manual.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF for oscilloscope - getting started with python
@app.route('/informations/oscilloscope_python')
def informations_oscilloscope_python():
    try:    
        path = "/home/student/webserver/informations/tektronix_mso6_python.pdf"
        return send_file(path)
        
    except TypeError:
        return informations()

# PDF - DC Bias table
@app.route('/informations/dc_bias_table')
def dc_bias_table():

    try:    
        path = "/home/student/webserver/informations/dc_bias_table.pdf"
        return send_file(path)
        
    except TypeError:
        return instructions()

# PDF - compensation instruction
@app.route('/informations/compensation_info')
def compensation_info():

    try:    
        path = "/home/student/webserver/informations/compensation_info.pdf"
        return send_file(path)
        
    except TypeError:
        return instructions()

# PDF - moving csv to excel instrucion
@app.route('/informations/csv_to_excel')
def csv_to_excel():

    try:    
        path = "/home/student/webserver/informations/csv_to_excel.pdf"
        return send_file(path)
        
    except TypeError:
        return instructions() 


### RLC  BRIDGE PAGE ###

# Main RLC route
@app.route('/rlc_bridge', methods=['GET', 'POST'])
def rlc_bridge():
    connection = bridge_class.rlc_connect()
    prg_number = 0
    formv4 = ResetForm()
    formv5 = ConnectionForm()

    data_ready = 'Nie'

    # If automatically not connected going to redirect to connect
    if formv5.submitv5.data and formv5.validate_on_submit():
        connection = bridge_class.rlc_connect()
        return redirect('/rlc_bridge')
      
    # Reset
    if formv4.submitv4.data and formv4.validate_on_submit():
        bridge_class.reset(connection)
        session.pop("rlc_bridge", None)
         
    if connection == 'Nie połączono':
        connection = ['Nie połączono', 'Nie połączono']
    
    template_data = {
        'data_ready': f'{data_ready}',
        'rlc_info'   : f'{bridge_class.rlc_info(connection)}',
        'number_prog': f'{prg_number}',
        'formv4' : formv4, 
        'formv5' : formv5,           
        }
    return render_template('rlc_bridge.html', **template_data)

# Compens RLC route
@app.route('/rlc_bridge_compens', methods=['GET', 'POST'])
def rlc_bridge_compens():

    connection = bridge_class.rlc_connect()
    formv3 = CompensationForm()

    # Compensation form
    if formv3.submitv3.data and formv3.validate_on_submit():

        try:
            connection = bridge_class.rlc_connect()
            witch_comp = formv3.compensation_choose.data
            compens = bridge_class.compensation(connection, witch_comp)
        except:
            return render_template('rlc_bridge_compensation_error.html')
        
        if compens == 'Error':
            print('BLAD')
            return render_template('rlc_bridge_compensation_error.html')
        session.pop("rlc_bridge", None)

    template_data = {
        'formv3' : formv3,      
        }
    return render_template('rlc_bridge_compensation.html', **template_data)


# Settings RLC route
@app.route('/rlc_bridge_settings', methods=['GET', 'POST'])
def rlc_bridge_settings():
    connection = bridge_class.rlc_connect()
    form = RlcForm()

    # Settings form
    if form.submitv1.data and form.validate_on_submit():
        prg_number = form.program_number.data
        meas_speed = form.measurement_speed.data 
        circ_type = form.circuit_type.data
        circ_range = form.circuit_range.data
        volt = form.voltage.data

        # DC bias
        dc_bias = form.dc_bias.data
        dc_bias_volt = form.dc_bias_voltage.data
        dc_bias_curr = form.dc_bias_current.data
        print(type(dc_bias_curr))

    # Settings
    try:
        connection = bridge_class.rlc_connect()
        bridge_class.witch_program(connection,prg_number)
        bridge_class.measurement_speed(connection, meas_speed)
        # bridge_class.frequency_range(freq_range)
        bridge_class.circuit_type(connection, circ_type)
        bridge_class.circuit_range(connection, circ_range)
        if dc_bias == '0':
            bridge_class.voltage(connection, volt)
            bridge_class.dc_bias(connection, dc_bias, dc_bias_volt, float(dc_bias_curr), prg_number)
        else:
            bridge_class.dc_bias(connection, dc_bias, dc_bias_volt, float(dc_bias_curr), prg_number)
    except:
        pass

    template_data = {
        'form' : form,      
        }
    return render_template('rlc_bridge_settings.html', **template_data)

# Automat measurement RLC route
@app.route('/rlc_bridge_measur', methods=['GET', 'POST'])
def rlc_bridge_measur():
    connection = bridge_class.rlc_connect()
    formv6 = MakeMeasurementForm()
    formv2 = DownloadForm()
    formv7 = DownloadCharacteristicForm()
    formv8 = DownloadCharacteristicv2Form()

    # Make measurement
    if formv6.submitv6.data and formv6.validate_on_submit():
        try:
            # Without connecting one more time measurment some times has failed
            connection = bridge_class.rlc_connect()
            # Continue making measurement
            make_csv = formv6.make_csv.data
            freq_range = formv6.frequency_range.data
            snd_mail = formv6.send_email.data
            interv_samples = formv6.interval_between_samples.data
            bridge_class.frequency_range(freq_range)

            # Make measurement
            bridge_class.make_measurement(connection, freq_range, float(interv_samples))
            if make_csv == '1':
                bridge_class.make_csv(connection)

            #Make plot nr.1
            bridge_class.plot_char(freq_range, connection)
            # #Make plot nr.2
            bridge_class.plot_charv2(freq_range, connection)


            if snd_mail:
                bridge_class.send_mail(snd_mail)
        except:
            pass
    # Download form csv
    if formv2.submitv2.data and formv2.validate_on_submit():
        
        dwnl_file = formv2.download_file.data
        if dwnl_file == '1':
            return redirect('rlc_bridge/download')
        else:
            pass

    # Download form characteristic nr.1 
    if formv7.submitv7.data and formv7.validate_on_submit():
        try:
            dwnl_file = formv7.download_file_char.data
            if dwnl_file == '1':
                return redirect('rlc_bridge/download_characteristic')
        except:
            pass
     
    # Download form characteristic nr.2
    if formv8.submitv8.data and formv8.validate_on_submit():
        try:
            dwnl_file = formv8.download_file_char.data
            if dwnl_file == '1':
                return redirect('rlc_bridge/download_characteristicv2')
        except:
            pass
            return redirect('/rlc_bridge')

    template_data = {
        'formv6' : formv6,
        'formv2' : formv2,
        'formv7' : formv7,
        'formv8' : formv8,    
        }
    return render_template('rlc_bridge_measurement.html', **template_data)

# Download csv route
@app.route('/rlc_bridge/download', methods=['GET', 'POST'])
def rlc_bridge_download():
    path = 'data/rlc_data.csv'
    return send_file(path, as_attachment=True)

# Download characteristic nr. 1
@app.route('/rlc_bridge/download_characteristic', methods=['GET', 'POST'])
def rlc_bridge_download_characteristic():
    try:
        path2 = 'data/characteristic.png'
        return send_file(path2, as_attachment=True)
    except:
        return redirect('/rlc_bridge')

# Download characteristic nr. 2
@app.route('/rlc_bridge/download_characteristicv2', methods=['GET', 'POST'])
def rlc_bridge_download_characteristicv2():
    try:
        path3 = 'data/characteristic_nr2.png'
        return send_file(path3, as_attachment=True)
    except:
        return redirect('/rlc_bridge')


### POWER SUPPLY DELTA ELEKTRONIKA SM1500-CP-30 ###

# Power Supply device temporary data
ps_device_connect_data= ['Nie połączono']
ps_device_info_data=['']
ps_device_temp_data=['']
ps_device_volt_data=['']
ps_device_curr_plus_data=['']
ps_device_curr_minus_data=['']
ps_device_power_data=['']
ps_device_error_status_data=['']
ps_device_warning_status_data=['']

# Main power supply route
@app.route('/delta_supply_sm1500', methods=['GET', 'POST'])
def delta_supply_sm1500():


    # Power supply forms
    form = PSReset()
    form2 = PSCheck()
    form3 = PSSettings()

    # Variables for first website start
    info_about_connect = ''
    info_about_device = ''

    # Try connect if device is available - if not will took more time cause of visa connect
    try:
        # Connecting
        
        info_about_connect = power_supply_class.connect_to_ps()
        

        # Status
        power_supply_class.info_ps(info_about_connect)
        # ps_device_connect_data.clear() ??
        ps_device_connect_data.append('Połączono')
        
        # Info
        info_about_device = power_supply_class.info_ps(info_about_connect)
        ps_device_info_data.append(info_about_device)

        # Temperature
        info_about_temp = power_supply_class.temperature_ps(info_about_connect)
        # ps_device_temp_data.clear() ??
        ps_device_temp_data.append(info_about_temp)

        # Volt
        info_about_volt = power_supply_class.voltage_ps(info_about_connect)
        ps_device_volt_data.append(info_about_volt)

        # Current +
        info_about_curr_plus = power_supply_class.current_plus_ps(info_about_connect)
        ps_device_curr_plus_data.append(info_about_curr_plus)

        # Current -
        info_about_curr_minus = power_supply_class.current_minus_ps(info_about_connect)
        ps_device_curr_minus_data.append(info_about_curr_minus)

        # Power
        info_about_power = power_supply_class.power_ps(info_about_connect)
        ps_device_power_data.append(info_about_power)

        # Error
        info_about_error_status = power_supply_class.error_status_ps(info_about_connect)
        ps_device_error_status_data.append(info_about_error_status)

        # Warning
        info_about_warning_status = power_supply_class.worning_status_ps(info_about_connect)
        ps_device_warning_status_data.append(info_about_warning_status)

        # On normal form doesnt work
        # Output true
        if form3.output.data == '2' and form3.validate_on_submit():
            info_about_connect[1].write(f"OUTPut 1")

        # Output fasle
        if form3.output.data == '1' and form3.validate_on_submit():
            info_about_connect[1].write(f"OUTPut 0")
        
        # Output power
        if form3.validate_on_submit():
            power = form3.power.data
            power_supply_class.power_input_ps(info_about_connect, float(power))

            # Changing info about data set in power supply
            ps_device_power_data[1] = power_supply_class.power_ps(info_about_connect)


    # Except if power supply is not connected
    except:
        return render_template('error_404.html')

    # Reset button
    if form.submit1.data and form.validate_on_submit():
        try:
            power_supply_class.reset_ps(info_about_connect)

            # Clearing data to start values
            ps_device_connect_data.clear()
            ps_device_info_data.clear()
            ps_device_temp_data.clear()
            ps_device_volt_data.clear()
            ps_device_curr_plus_data.clear()
            ps_device_curr_minus_data.clear()
            ps_device_power_data.clear()
            ps_device_error_status_data.clear()
            ps_device_warning_status_data.clear()

            return redirect('delta_supply_sm1500')
        except:
            return redirect('delta_supply_sm1500')
    
    # Check button
    # If available - device will blink and make noise
    if form2.submit2.data and form2.validate_on_submit():
        try:
            power_supply_class.check_ps(info_about_connect)
            return redirect('delta_supply_sm1500')
        except:
            return redirect('delta_supply_sm1500')
    
    # Device settings
    if form3.submit3.data and form3.validate_on_submit():
        try:
            # User data from form
            volt = form3.voltage.data
            curr_plus = form3.current_plus.data
            curr_minus = float(form3.current_minus.data)

            # Info if number is + not -
            if curr_minus >= 0:
                curr_minus = 'Liczba musi być ujemna'
            
            # Info if number is + not -
            if curr_plus < 0:
                curr_plus = 'Liczba musi być nieujemna'
            
            # Changing info about data set in power supply
            ps_device_volt_data[1] = volt
            ps_device_curr_plus_data[1] = curr_plus
            ps_device_curr_minus_data[1] = curr_minus

            # Functions from power supply program
            power_supply_class.voltage_input_ps(info_about_connect, float(volt))
            power_supply_class.currnet_plus_input__ps(info_about_connect, float(curr_plus))
            power_supply_class.currnet_minus_input_ps(info_about_connect, float(curr_minus))
            power_supply_class.power_input_ps(info_about_connect, float(power))
            
            return redirect('delta_supply_sm1500')
        except:
            return redirect('delta_supply_sm1500')
    
    try:
        template_data = {
        'form': form,   
        'form2': form2,
        'form3': form3,
        'info_about_connect': ps_device_connect_data[1] ,
        'info_about_device': ps_device_info_data[1],
        'info_about_temp': ps_device_temp_data[1],
        'info_about_volt': ps_device_volt_data[1],
        'info_about_curr_plus': ps_device_curr_plus_data[1],
        'info_about_curr_minus': ps_device_curr_minus_data[1],
        'info_about_power': ps_device_power_data[1],
        'info_about_error': ps_device_error_status_data[1],
        'info_about_warning': ps_device_warning_status_data[1]
        }
    except:
        return redirect('delta_supply_sm1500')
        
    return render_template('delta_supply_sm1500.html', **template_data)

### OSCILLOSCOPE TEKTRONIX MSO6 ###

# Main oscilloscope route
@app.route('/main_oscilloscope', methods=['GET', 'POST'])
def oscilloscope_home():

    # Oscilloscope forms
    form = OSCReset()
    form2 = OSCConnect()

    # Connection
    try:
        osc_connect = oscilloscope_class.connect_to_oscilloscope()
    except:
        return render_template('error_404.html')

    # Reset button
    if form.submit.data and form.validate_on_submit():
        oscilloscope_class.reset_oscilloscope(osc_connect)
        return redirect('/main_oscilloscope')

    #Connect button
    if form2.submit2.data and form2.validate_on_submit():
        oscilloscope_class.connect_to_oscilloscope()
        return redirect('/main_oscilloscope')

    template_data = {
        'form': form,   
        'form2': form2,
    }
    return render_template('main_oscilloscope.html', **template_data)

# Oscilloscope characteristic
@app.route('/oscilloscope_characteristic', methods=['GET', 'POST'])
def oscilloscope_characteristic():

    # Oscilloscope characteristic forms
    form = OSCCHAR()
    formv2 = OSCCHARDownload()

    # Connection
    try:
        osc_connect = oscilloscope_class.connect_to_oscilloscope()
    except:
        return render_template('error_404.html')

    # Main form
    if form.submit.data and form.validate_on_submit():
 
        which_channel = form.which_channel.data
        vertical_scale = form.vertical_scale.data
        horizontal_scale = form.horizontal_scale.data
        send_email = form.send_email.data
        print(send_email)
        try:
            oscilloscope_class.get_plot_from_oscilloscope(osc_connect,which_channel,
                                                    vertical_scale, horizontal_scale)
        except:
            return render_template('wrong_oscilloscope_scale.html')
        if send_email != '':
            oscilloscope_class.send_mail(send_email)
    if formv2.submit2.data and formv2.validate_on_submit():
        return redirect('/oscilloscope_characteristic_download')

    template_data = {
        'form': form, 
        'formv2': formv2,
        }   
    return render_template('oscilloscope_char.html', **template_data)

# Download characteristic from oscilloscopee
@app.route('/oscilloscope_characteristic/download', methods=['GET', 'POST'])
def oscilloscope_characteristic_download():
    path = 'data/tektronix_oscilloscope.png'
    return send_file(path, as_attachment=True)

# Oscilloscope data logger
@app.route('/oscilloscope_data_logger', methods=['GET', 'POST'])
def oscilloscope_data_logger():

    # Oscilloscope characteristic forms
    form = OSCDataLogger()
    formv2 = OSCDataLoggerDownload()

    # Connection
    try:
        osc_connect = oscilloscope_class.connect_to_oscilloscope()
    except:
        return render_template('error_404.html')

    # Main form
    if form.submit.data and form.validate_on_submit():
        how_many_seconds = form.how_many_seconds.data
        which_channel = str(form.which_channel.data)
        send_email = form.send_email.data
    
        oscilloscope_class.data_logger(osc_connect,how_many_seconds, which_channel)

        if send_email:
            oscilloscope_class.send_csv_mail(send_email)
    if formv2.submit2.data and formv2.validate_on_submit():
        return redirect('/oscilloscope_data_logger/download')

    template_data = {
        'form': form, 
        'formv2': formv2,
        }   
    return render_template('oscilloscope_data_logger.html', **template_data)

# Oscilloscope csv download
@app.route('/oscilloscope_data_logger/download', methods=['GET', 'POST'])
def oscilloscope_data_logger_download():
    path = 'data/oscilloscope_data_logger.csv'
    return send_file(path, as_attachment=True)
#############################################################################################

                                ### PRESENTATION PAGE ###

#############################################################################################

# Home presentation page
@app.route('/home_presentation')
def home_presentation():
    template_data = {
        'cpu_temp' : f'Temperatura CPU: {temperature_of_raspberry_pi()}',
        'date': f'Data: {actual_date_time()[1]}',
        'time': f'Czas: {actual_date_time()[0]}'
        }   
    return render_template('home_presentation.html', **template_data)

# Temperature sensor page
@app.route('/temp_sens', methods =["GET", "POST"])
def temp_sens():
    
    # Global variables
    global how_many_temp_data, how_many_temp_sec, user_mail, status
    
    # Declarating variables for first open site
    how_many_temp_data = None
    how_many_temp_sec = None
    user_mail = None #'Dane nie zostaly wprowadzone lub sa przetwarzane'
    status = 'Wprowadz liczbe pomiarow oraz czas co jaki ma byc pobierana próbka!' + '\n'+  'Jeżeli wykonałeś/aś pomiary wyślij je na swojego maila lub pobierz.' 

    form =TempForm()
    if form.validate_on_submit():
        how_many_temp_data = form.how_many_temp_data.data 
        how_many_temp_sec = form.how_many_temp_sec.data
        status = 'Dane zostaly wprowadzone! Wykonaj pomiary.'

    form_send_mail =TempFormSendMail()
    if form_send_mail.validate_on_submit():
        user_mail = form_send_mail.user_mail.data 

    # While no signal from 1 wire temp sensor
    try:
        temperature_ds_temp = ds_temp()
    except:
        temperature_ds_temp = 'Brak sygnału od czujnika ?'

    template_data = {
        'title' : 'Czujnik temperatury',
        'button_start' : 'Start',
        'ds_sens_temp' : f'{temperature_ds_temp}',
        'status' : f'{status}',
        'wpisane_sec' : f'{how_many_temp_sec}',
        'form': form,
        'form_send_mail': form_send_mail
        }
    return render_template('temp_sens.html', **template_data)


# Making measurements - temp sensor
@app.route("/temp_sens/get_data_temp_sens", methods =["GET", "POST"])
def get_data_temp_sens():
    try:
        sens_temp.temperature_measurements(how_many_temp_data, how_many_temp_sec)
        return redirect("/temp_sens")
    except NameError or TypeError:
        return redirect("/temp_sens")
    
# Downloading txt with measurements
@app.route("/temp_sens/txt_temp", methods =["GET", "POST"])
def get_csv():
    try:    
        txt=sens_temp.txt
        return Response(
            txt,
            mimetype="text/txt",
            headers={"Content-disposition":
                    "attachment; filename=temp_sens_data.txt"})
        
    except TypeError:
        return redirect("/temp_sens")
    
# Sending email with measurements
@app.route("/temp_sens/send_mail", methods =["GET", "POST"])
def send_mail():
    
    try:
        
        # Email Data
        SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
        SMTP_PORT = 587 #Server Port (don't change!)
        EMAIL_USERNAME = 'energoelektronika.lab@gmail.com' #change this to match your gmail account
        EMAIL_PASSWORD = 'jsev rxmn wdlv fkdb' #change this to match your gmail app-password

        # From, To, Date, Subject - of email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = user_mail
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Dane pomiarowe - czujnik temperatury DS18B20'

        msg.attach(MIMEText('Wiadomosc wygenerowana automatycznie.\nW zalaczniku plik z pomiarami.'))

        
        part = MIMEBase('application', "octet-stream")
        with open('/home/student/webserver/data/temp_sens_data.txt', 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path('/home/student/webserver/data/temp_sens_data.txt').name))
        msg.attach(part)

        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_USERNAME, user_mail, msg.as_string())
        smtp.quit()
        status = 'Dane zostaly wysłane na maila wraz z załącznikiem!'
        return redirect("/temp_sens")
    except smtplib.SMTPRecipientsRefused or TypeError or NameError:
        return redirect("/temp_sens")
    
# Humidity sensors
@app.route('/humidity_sens') 
def humidity_sens():
    template_data = {
        'title' : 'Czujnik wilgotnosci',
        }  
    return render_template('humidity_sens.html', **template_data)

# Led control page
@app.route('/led_control')
def led_control():   
    template_data = {
        'title' : 'Swiatlo LED',
        'button_start' : 'Włącz',
        'button_stop' : 'Wyłącz',
        } 
    return render_template('led_control.html', **template_data)

# Controling led mechanics
@app.route('/<action>')
def led_ctrl(action):
    # Led on or off
    if action == 'led_on':
        led_control_on()
    elif action == 'led_off':
        led_control_off()
    #If user type something like that 192.168.0.1:5000/djsbakdhabsd (that is handler)
    else:
        return redirect('/')

    template_data = {
        'title' : 'Swiatlo LED',
        'button_start' : 'Włącz',
        'button_stop' : 'Wyłącz',
        } 
    return render_template('led_control.html', **template_data)

# Documentation
@app.route('/documentation')
def documentation():
    template_data = {
        'title' : 'Dokumentacja'
        }  
    return render_template('documentation.html', **template_data)

# Instructions
@app.route('/instructions')
def instructions():
    template_data = {
        'title' : 'Instrukcje'
        }  
    return render_template('instructions.html', **template_data)      

# PDF - temperature sensor instruction
@app.route('/instructions/temp_sens')
def instructions_temp_sens():

    try:    
        path = "/home/student/webserver/instructions/czujnik_temperatury.pdf"
        return send_file(path)
        
    except TypeError:
        return instructions() 

# Search form
@app.context_processor
def main():
    form_search =SearchForm()
    return dict(form_search=form_search)

# What to serach
@app.route('/search', methods=["POST"])
def search():


    form_search =SearchForm()
    if form_search.validate_on_submit():      
        searched = form_search.searched.data      
        linki={'instrukcje':'/instructions',
            'dokumentacja':'/documentation',
            'czujnik': '/temp_sens',
            'temperatury': '/temp_sens',
            'swiatlo': '/led_control',
            'led': '/led_control',
            'wilgotnosci' : '/humidity_sens',
            '' : '/home',
            'info':'/informations',
            'informations':'/informations',
            'manual':'/informations',
            'help':'/informations',
            'pomoc':'/informations',
            'rlc':'/rlc_bridge',
            'mostek':'/rlc_bridge',
            'zasilacz':'/delta_supply_sm1500',
            'power':'/delta_supply_sm1500',
            'supply':'/delta_supply_sm1500',
            'delta':'/delta_supply_sm1500',
            'oscyloskop':'/main_oscilloscope',
            'oscilloscope':'/main_oscilloscope',
            'tektronix':'/main_oscilloscope',
            'mso6':'/main_oscilloscope'
            }
        
# Checking if 3 first letters are same like key in dick then rendering a value with is in this case .html

        for i in linki:
            if searched[0:3].lower() == i[0:3]:       
                #return render_template(f'{linki[i]}', form=form)
                return redirect(f'{linki[i]}')

# If nothing is typed but button was pressed
    return redirect('/')

# Thermocouple
@app.route('/thermocouple')
def thermocouple():
    template_data = {
        'dane' : f'{thermocouple_temp()}'
        }  
    return render_template('thermocouple.html', **template_data)  


if __name__ == "__main__":
   app.secret_key = 'secret key'
   app.run(host='0.0.0.0', port=5000, debug=True)
   

