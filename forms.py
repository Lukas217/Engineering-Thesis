from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField, IntegerField, EmailField, SelectField, FloatField, validators, HiddenField, RadioField, DecimalField
from wtforms.validators import DataRequired



# Search 
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Wyszukaj")

### PRESENTATION PAGE

# Temperature 
class TempForm(FlaskForm):
    how_many_temp_data = IntegerField("Podaj liczbe pomiarow", validators=[DataRequired()])
    how_many_temp_sec = IntegerField("Podaj czas", validators=[DataRequired()])
    submit = SubmitField("Wpisz")

# Send temperature data to email
class TempFormSendMail(FlaskForm):
    user_mail = EmailField("Podaj email", validators=[DataRequired()])
    submit = SubmitField("Wpisz")

### AUTOMATION PAGE

# RLC FORMS

# Main
class RlcForm(FlaskForm):
    program_number = SelectField("Rodzaj pomiaru",
    choices=[(0, 'Auto'), (1, 'L-Q'), (2, 'L-R'),(3, 'C-D'), (4, 'C-R'), (5, 'R-Q'),
            (6, 'Z-Θ'), (7, 'Y-Θ'), (8, 'R-X'), (9, 'G-B'), (10, 'N-Θ'), (11, 'M')])
    measurement_speed = SelectField("Szybkość pomiaru", choices=[(0, 'Szybko'),(1, 'Średnio'), (2, 'Wolno')])
    circuit_type = SelectField("Typ obwodu", choices=[(0, 'Szeregowy'), (1, 'Równoległy'), (2, 'Auto')])
    circuit_range = SelectField("Zakres pomiarowy", choices=[(0, 'Auto'),(1, '1-25Ω'), (2, '2-25Ω'),
                                                         (3, '3-400Ω'), (4, '4-6.4kΩ'), (5, '5-100kΩ'), (6, '6-100kΩ')])
    voltage = FloatField("*Napięcie pomiarowe (0.05V - 1.5V)", [validators.Optional()])
    dc_bias = RadioField("DC BIAS:",default=0, choices=[(0, 'Nie'),(1, 'Wewnętrzny'),(2, 'Zewnętrzny') ])
    dc_bias_voltage = IntegerField("*DC bias - napięcie (0V - 5V)", [validators.Optional()])
    dc_bias_current = FloatField("*DC bias - prąd (0.001A - 0.200A)", [validators.Optional()])
    submitv1 = SubmitField("Wyślij")

# Download
class DownloadForm(FlaskForm):
    download_file = SelectField("Pobierz plik .csv", choices=[(1, 'Tak'),(2, 'Nie')])
    submitv2 = SubmitField("Pobierz")

# Download characteristic nr. 1
class DownloadCharacteristicForm(FlaskForm):
    download_file_char = SelectField("Pobierz charakterystyke nr.1", choices=[(1, 'Tak'),(2, 'Nie')])
    submitv7 = SubmitField("Pobierz")

# Download characteristic nr. 2
class DownloadCharacteristicv2Form(FlaskForm):
    download_file_char = SelectField("Pobierz charakterystyke nr.2", choices=[(1, 'Tak'),(2, 'Nie')])
    submitv8 = SubmitField("Pobierz")

# Compensation
class CompensationForm(FlaskForm):
    compensation_choose = SelectField("Wybierz rodzaj kompensacji", choices=[(1, 'Otwarta'),(2, 'Zamknieta')])
    submitv3 = SubmitField("Wykonaj")

# Reset
class ResetForm(FlaskForm):
    submitv4 = SubmitField("Zresetuj urządzenie")

# Connection
class ConnectionForm(FlaskForm):
    submitv5 = SubmitField("Połącz z urządzeniem")

# Measurement                                                 
class MakeMeasurementForm(FlaskForm):
    frequency_range = SelectField("Zakres pomiaru", choices=[(0, 'Duży'),(1, 'Średni'), (2, 'Mały')])
    interval_between_samples = SelectField("Czas pomiędzy próbkami", choices=[(0.6, '0.6s'),(0.8, '0.8s'),(1, '1s'),(2, '2s'), (3, '3s')])
    make_csv = SelectField("Utwórz plik .csv", choices=[(1, 'Tak'),(2, 'Nie')])
    send_email = EmailField("*Podaj email")
    submitv6 = SubmitField("Wykonaj i wyślij")


# POWER SUPPLY FORMS

# PSReset - Power supply connect
class PSReset(FlaskForm):
    submit1 = SubmitField("Resetuj")

#PSInfo - Power supply check - buzzer and blink
class PSCheck(FlaskForm):
    submit2 = SubmitField("Sprawdź")

#PSSettings - Power supply settings
class PSSettings(FlaskForm):
    voltage = FloatField("Podaj napięcie", validators=[DataRequired()])
    current_plus = FloatField("Podaj prąd dodatni", validators=[DataRequired()])
    current_minus = FloatField("Podaj prąd ujemny", validators=[DataRequired()])
    power = FloatField("Podaj moc", [validators.Optional()])
    output = SelectField("Wyjście", choices=[(1, 'Wyłącz'),(2, 'Włącz')])
    submit3= SubmitField("Wyślij")

# OSCILLOSCOPE FORMS

# MAIN 

# OSCConnect - Oscilloscope supply connect
class OSCReset(FlaskForm):
    submit = SubmitField("Resetuj")

# OSCConnect - Connection to oscilloscope
class OSCConnect(FlaskForm):
    submit2 = SubmitField("Połącz")

# CHARACTERISTIC

# OSCCHARChannel - Which channel, Vertical Scale, Horizontal Scale, Send Mail?, Confirm button
class OSCCHAR(FlaskForm):
    which_channel = SelectField("Kanał", choices=[(1, '1'),(2, '2'),(3, '3'),(4, '4'),(5, '5'),(6, '6'),(7, '7'),(8, '8')])
    vertical_scale = StringField("Pionowa skala", validators=[DataRequired()])
    horizontal_scale = StringField("Pozioma skala", validators=[DataRequired()])
    send_email = EmailField("*Podaj email")
    submit = SubmitField("Utwórz")

class OSCCHARDownload(FlaskForm):
    submit2 = SubmitField("Pobierz")

# DATA LOGGER

class OSCMakeCsv(FlaskForm):
    send_email = EmailField("*Podaj email")
    submit2 = SubmitField("Zbierz dane")

class OSCDataLogger(FlaskForm):
    which_channel = SelectField("Kanał", choices=[(1, '1'),(2, '2'),(3, '3'),(4, '4'),(5, '5'),(6, '6'),(7, '7'),(8, '8')])
    how_many_seconds = IntegerField("Ile pomiarów?")
    send_email = EmailField("*Podaj email")
    submit = SubmitField("Utwórz")

class OSCDataLoggerDownload(FlaskForm):
    submit2 = SubmitField("Pobierz")

