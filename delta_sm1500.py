import pyvisa

# Power supply
class PSDelta():

    # Connection
    def connect_to_ps(self):
     
        rm = pyvisa.ResourceManager('@py')
       
        ps_delta = rm.open_resource('TCPIP0::192.168.0.20::8462::SOCKET', read_termination='\n', open_timeout=1000)
        wynik = 'Połączono z zasilaczem'

        return wynik, ps_delta

    ### QUERY FROM DEVICE ###

    # Info
    def info_ps(self, ps_delta):
            ps_info = ps_delta[1].query("*IDN?")
            return ps_info
    
    # Temperature
    def temperature_ps(self, ps_delta):
            ps_temperature = ps_delta[1].query("MEASURE:TEMperature?")
            return ps_temperature
    
    # Voltage
    def voltage_ps(self, ps_delta):
            ps_voltage = ps_delta[1].query("SOURCE:VOLtage?")
            return ps_voltage

    # Current +
    def current_plus_ps(self, ps_delta):
                ps_current_plus = ps_delta[1].query("SOURCE:CURrent?")
                return ps_current_plus

    # Current - 
    def current_minus_ps(self, ps_delta):
                ps_current_minus = ps_delta[1].query("SOURCE:CURrent:NEGATIVE?")
                return ps_current_minus

    # Power
    def power_ps(self, ps_delta):
                ps_power = ps_delta[1].query("SOURCE:POWer?")
                return ps_power
    
    # Error status
    def error_status_ps(self, ps_delta):
                ps_error_status = ps_delta[1].query("SYSTem:ERRor?")
                return ps_error_status

    # Warning status
    def worning_status_ps(self, ps_delta):
                ps_warning_status = ps_delta[1].query("SYSTem:Warning?")
                return ps_warning_status

    ### WRITE TO DEVICE ###

    # Reset
    def reset_ps(self, ps_delta):
        ps_reset = ps_delta[1].write("*RST")
        return ps_reset
    
    # Check    
    def check_ps(self, ps_delta):
        ps_check = ps_delta[1].write("SYSTem:FROntpanel:HIGhlight")
        return ps_check
    
    # Voltage - user input
    def voltage_input_ps(self, ps_delta, user_input):
        ps_voltage= ps_delta[1].write(f"SOURCE:VOLtage {user_input}")
        return ps_voltage

    # Current plus - user input
    def currnet_plus_input__ps(self, ps_delta, user_input):
        ps_current_plus= ps_delta[1].write(f"SOURCE:CURrent {user_input}")
        return ps_current_plus
    
    # Current minus - user input
    def currnet_minus_input_ps(self, ps_delta, user_input):
        ps_current_minus= ps_delta[1].write(f"SOURCE:CURrent:NEGATIVE {user_input}")
        return ps_current_minus
    
    # Power - user input
    def power_input_ps(self, ps_delta, user_input):

        ps_power = ps_delta[1].write(f"SOURCE:POWer {user_input}")
        return ps_power

