from machine import Pin, SPI, reset
import config
import led

LORA_RESET_PIN = 4  

LORA_SS_PIN = 15
LORA_SCK_PIN = 14
LORA_MOSI_PIN = 13
LORA_MISO_PIN = 12

LORA_IRQ_PIN = 5 


class mock:
    pass   

def prepare_pin(pin_id, in_out = Pin.OUT):
    pin = Pin(pin_id, in_out)
    new_pin = mock()
    new_pin.value = pin.value
    
    if in_out == Pin.OUT:
        new_pin.low = lambda : pin.value(0)
        new_pin.high = lambda : pin.value(1)        
    else:
        new_pin.irq = pin.irq
        
    return new_pin

def prepare_irq_pin(pin_id): 
    pin = prepare_pin(pin_id, Pin.IN) 
    pin.set_handler_for_irq_on_rising_edge = lambda handler: pin.irq(handler = handler, trigger = Pin.IRQ_RISING)
    pin.detach_irq = lambda : pin.irq(handler = None, trigger = 0)
    return pin

def prepare_spi(spi):       
    ss = prepare_pin(LORA_SS_PIN)
    ss.high()
    spi.init()               
    new_spi = mock()  

    def transfer(address, value = 0x00):        
        response = bytearray(1)

        ss.low()
         
        spi.write(bytes([address]))
        spi.write_readinto(bytes([value]), response)

        ss.high()

        return response
        
    new_spi.transfer = transfer
    
    return new_spi

    
if config.IS_ESP8266:
    spi = SPI(1, baudrate = 10000000, polarity = 0, phase = 0)        
    
if config.IS_ESP32:
    try:
        spi = SPI(1, baudrate = 10000000, polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
                  sck = Pin(LORA_SCK_PIN, Pin.OUT), 
                  mosi = Pin(LORA_MOSI_PIN, Pin.OUT), 
                  miso = Pin(LORA_MISO_PIN, Pin.IN)) 
    except Exception as e:
        print(e)
        reset()  # in case SPI is already in use, need to reset. 
        
    
    
class Controller:
        
    def __init__(self, 
                 reset_pin_id = LORA_RESET_PIN, 
                 irq_pin_id = LORA_IRQ_PIN):
                 
        self.reset_pin = prepare_pin(reset_pin_id)
        self.irq_pin = prepare_irq_pin(irq_pin_id)if irq_pin_id else None  
        self.spi = prepare_spi(spi)
        self.blink_led = led.blink_on_board_led
                  

        

        
        


        
 
        
