"""Clock learning app"""

from scene import *
import ui
from math import *
from datetime import datetime
import random
import speech
import time
import string

CONST_BACKGROUNDCOLOR = '#cc8800'
CONST_FACECOLOR = '#fff0d3'
CONST_TEXTCOLOR = '#6d4900'
CONST_BORDERCOLOR = '#6d4900'


def calculate_angle(vertex, position):
    # centre:
    # B Vertex
    # C Endpoint line 2

    x1, y1 = (vertex[0], vertex[1] + 100)  # Referece line from center right up
    x2, y2 = vertex  # Centre position
    x3, y3 = position  # Position of 2nd line>

    # Vectors BA and BC
    BA = (x1 - x2, y1 - y2)
    BC = (x3 - x2, y3 - y2)

    # Dot product and magnitudes
    dot_product = BA[0] * BC[0] + BA[1] * BC[1]
    magnitude_BA = math.sqrt(BA[0]**2 + BA[1]**2)
    magnitude_BC = math.sqrt(BC[0]**2 + BC[1]**2)

    # Calculate the cosine of the angle
    cosine_angle = dot_product / (magnitude_BA * magnitude_BC)
    angle_radians = math.acos(cosine_angle)

    # Calculate the cross product to determine the angle orientation
    cross_product = BA[0] * BC[1] - BA[1] * BC[0]
    if cross_product > 0:
        # If cross product is negative, the angle is greater than 180 degrees
        angle_radians = 2 * math.pi - angle_radians

    return angle_radians, int(math.degrees(angle_radians) / 6)

''' Shows a clock face, hands can move by a rotation gesture '''
class Clock(Scene):

    lesson_hours = 0
    lesson_minutes = 0
    lesson_count = 0
    lesson_todo = 2
    lesson_good = 0
    lesson_error = 0
        
    def setup(self):
        self.enabled = True
        self.background_color = CONST_BACKGROUNDCOLOR
        self.hours = 10
        self.minutes = 10
        
        # Radius of the circle: quarter of the smallest of width and depth
        radius = min(self.size) / 2 - 20
        circle = ui.Path.oval(0, 0, radius * 2, radius * 2)
        circle.line_width = 10
        self.circle = ShapeNode(circle, CONST_FACECOLOR, CONST_BORDERCOLOR)
        
        # Position of the circle: in the middle
        self.circle.position = (self.size / 2)
        self.add_child(self.circle)
        
        # Add hour labels
        for i in range(12):
            label = LabelNode(str(i+1), font=('HelveticaNeue', 0.15*radius))
            label.color = 'black'
            a = 2 * pi * (i+1)/12.0
            label.position = sin(a)*(radius*0.85), cos(a)*(radius*0.85)
            self.circle.add_child(label)
            
        # Add minute labels
        for i in range(60):
            if ((i + 1) % 5 != 0):
                shape = ShapeNode(ui.Path.rounded_rect(0, 0, 4, 4, 5), CONST_BORDERCOLOR)
                a = 2 * pi * (i+1)/60.0
                shape.position = sin(a)*(radius*0.85), cos(a)*(radius*0.85)
                self.circle.add_child(shape)
            
        # Add hour and minute hands
        self.hands = []
        hand_attrs = [(radius*0.6, 8, '#6d4900'), (radius*0.9, 8, CONST_BORDERCOLOR)]
        for length, width, color in hand_attrs:
            shape = ShapeNode(ui.Path.rounded_rect(0, 0, width, length, width/2), color)
            shape.anchor_point = (0.5, 0)
            self.hands.append(shape)
            self.circle.add_child(shape)
        self.circle.add_child(ShapeNode(ui.Path.oval(0, 0, 15, 15), 'black'))
        self.move_hands(10, 10)
        
    def did_change_size(self):
        # Reposition the circle in the middle
        self.circle, position = self.size / 2
    
    def enabled(e):
        self.enabled = e
        
    ''' Set the clock hands to this time '''
    def move_hands(self, hours, minutes):
        self.hands[1].rotation = 2 * math.pi * (minutes / -60)
        minute_part = (minutes / 60)
        self.hands[0].rotation = 2 * math.pi * ((hours + minute_part) / -12)
        
    
    ''' Move the clock hands '''    
    def touch_moved(self, touch):
        prev_minutes = self.minutes
        angle, self.minutes = calculate_angle(self.circle.position, touch.location)
        # Debouncing forward rotation
        if (prev_minutes > 55 and self.minutes < 5):
            self.hours = self.hours + 1
            if (self.hours == 13):
                self.hours = 1
        # Deboncing backward rotation
        if (prev_minutes < 5 and self.minutes > 55):
            self.hours = self.hours - 1
            if (self.hours == 0):
                self.hours = 12
        self.move_hands(self.hours, self.minutes)
        
          
    ''' Touch ended check the result
        The self.on_change function is replaced by a callback '''
    def touch_ended(self, touch):
        if (self.enabled):
            self.on_change(self)
            
    def on_change(self):
        pass


class TellTime():
    """
        TellTime class converts time digits (10:25) to text (twenty-five after ten)
        It has now support for English, Dutch and German
        In Dutch and German there are some differences in conversion, like 10:35 is "vijf over half 11"
        In English make a diffrence between midnight and noon
    """
    
    def __init__(self):
        self.units = (
                     ('noon', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                         'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
                         'seventeen', 'eighteen', 'nineteen', 'twenty',
                         'twenty-one', 'twenty-two', 'twenty-three', 'twenty-four', 'midnight'),
                     ('twaalf', 'één', 'twee', 'drie', 'vier', 'vijf', 'zes', 'zeven', 'acht',
                         'negen', 'tien', 'elf', 'twaalf', 'dertien', 'veertien',
                         'vijftien', 'zestien', 'zeventien', 'achttien', 'negentien',
                         'twintig', 'eenentwintig', 'tweeentwintig', 'drieentwintig', 'vierentwintig', 'twaalf'),
                     ('zwölf', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht',
                         'neun', 'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn', 'fünfzehn',
                         'sechzehn', 'siebsehn', 'achtzehn', 'neunzehn', 'zwanzig',
                         'einundzwanzig', 'zweiundzwanzig', 'dreiundzwanzig', 'vierundzwanzieg', 'zwölf')
                     )
        
        self.tens = (
                    ('', 'ten', 'twenty-', 'thirty-', 'fourty-', 'fifty-'),
                    ('', 'tien', 'twintig', 'derig', 'veertig', 'vijftig'),
                    ('', 'zehn', 'zwanzig', 'dreiẞig', 'vierzig', 'fünfzig')
                    )
        
        self.strings = (
                       (' ', 'minute ', 'minutes ', " o'clock", 'hours', 'to ', 'past ', 'quarter ', 'half '),
                       (' ', 'minuut ', 'minuten ', ' uur', 'uren', 'voor ', 'over ', 'kwart ', 'half '),
                       (' ', 'minute ', 'minuten ', ' Uhr ', 'Uhren ', 'vor ', 'nach ', 'viertel ', 'halb '))
                        
    def set_language(self, lang):
        match lang:
            case 'en_US': self.language = 0
            case 'nl_NL': self.language = 1
            case 'de_DE': self.language = 2
            case '_': self.language = 0
            
    def minutes_tell(self, m):
        """
            Numbers up to 20 sometimes spelled and pronounced differently:
            thirteen and not threeteen
            veertien and not viertien
            siebsehn and not siebensehn
            Thats why they are included in the tuple
        """
        minute_units = m % 10
        minute_tens = int(m / 10)
        if (m < 25):
            minutes = self.units[self.language][m] + ' '
        else:
            minutes = self.tens[self.language][minute_tens] + self.units[self.language][minute_units] + ' '
        return minutes
        
    def translate(self, hours, minutes, commands):
        command_list = commands.split(' ')
        s = ''
        for command in command_list:
            match command:
                case 'hour': 
                    s += self.units[self.language][25] if hours == 0 \
                    else self.units[self.language][hours % 12]
                case 'minutes_after_hour': s += self.minutes_tell(minutes)
                case 'minutes_to_half': s += self.minutes_tell(30 - minutes)
                case 'minutes_to_hour': s += self.minutes_tell(60 - minutes)
                case 'minutes_after_half': s += self.minutes_tell(minutes - 30)
                case 'next_hour': s += self.units[self.language][hours + 1]
                case 'MINUTE': s += self.strings[self.language][1]  # minute
                case 'MINUTES': s += self.strings[self.language][2]  # minutes
                case 'HOUR': s += self.strings[self.language][3]  # o'clock'
                case 'HOURS': s += self.strings[self.language][4]  # hours
                case 'TO': s += self.strings[self.language][5]  # to
                case 'PAST': s += self.strings[self.language][6]  # past
                case 'QUARTER': s += self.strings[self.language][7]  # quarter
                case 'HALF': s += self.strings[self.language][8]  # half
                case '_':  s += ' '
                case 'E':  s += 'Error'
        return s

    ''' lower case: value, upper case: text '''
    def tell(self, hours, minutes):
        """
           There are up to 8 distinct ways to pronounce minutes time,
               0, 1-14, 15, 16-29, 30, 31-44, 45, 46-59
        """
        match minutes:
            case 0: s = 'hour HOUR'
            case n if n in range(1, 15): s = 'minutes_after_hour PAST hour'
            case 15: s = 'QUARTER PAST hour'
            case n if n in range(16, 30): s = 'minutes_after_hour PAST hour' if self.language == 0 \
                else 'minutes_to_half TO HALF next_hour'
            case 30: s = 'HALF PAST hour' if self.language == 0 else 'HALF next_hour'
            case n if n in range(31, 45): s = 'minutes_after_hour PAST hour' if self.language == 0 \
                else 'minutes_after_half PAST HALF next_hour'
            case 45: s = 'QUARTER TO next_hour'
            case n if n in range(46, 60): s = 'minutes_to_hour TO next_hour'
            case _: s = 'Error'
            
         
        return self.translate(hours, minutes, s)


''' Generate a random time in hours '''
def mode_hours():
    prev_hours = clock.lesson_hours
    while (prev_hours == clock.lesson_hours):
        clock.lesson_hours = random.randint(1, 12)
    return tell_time.tell(clock.lesson_hours, clock.lesson_minutes)


''' Generate a random time in half hours '''
def mode_half_hours():
    clock.lesson_hours = random.randint(1, 11)
    prev_minutes = clock.lesson_minutes
    while (prev_minutes == clock.lesson_minutes):
        clock.lesson_minutes = random.randint(0, 1) * 30
    return tell_time.tell(clock.lesson_hours, clock.lesson_minutes)
 

''' Generate a time in quarter hours '''    
def mode_quarter_hours():
    clock.lesson_hours = random.randint(1, 11)
    prev_minutes = clock.lesson_minutes
    while (prev_minutes == clock.lesson_minutes):
        clock.lesson_minutes = random.randint(0, 3) * 15
    return tell_time.tell(clock.lesson_hours, clock.lesson_minutes)
 
''' Generate a time in increments of 5 minutes '''           
def mode_five_minutes():
    clock.lesson_hours = random.randint(1, 11)
    prev_minutes = clock.lesson_minutes
    while (prev_minutes == clock.lesson_minutes):
        clock.lesson_minutes = 5 * random.randint(0, 11)
    return tell_time.tell(clock.lesson_hours, clock.lesson_minutes)


''' Callback function to show results '''
def check_result(self):
    self.lesson_count += 1
    if ((self.lesson_hours == self.hours) and (self.lesson_minutes == self.minutes)):
        v['result_label'].text = '👍'
        self.lesson_good += 1
    else:
        v['result_label'].text = '👎'
        self.lesson_error += 1
        
    if (self.lesson_count == self.lesson_todo):
        if (self.lesson_good == self.lesson_todo):
            v['result_label'].text = '🥇'
        elif (self.lesson_good > self.lesson_todo * 0.7):
            v['result_label'].text = '🥈'
        elif (self.lesson_good > self.lesson_todo * 0.5):
            v['result_label'].text = '🥉'
        else:
            v['result_label'].text = '🎲'
        v['reset_button'].alpha = 1
        v['start_button'].alpha = 0
        
    v['score_label'].text = str(self.lesson_good) + ' - ' + str(self.lesson_error)
    clock.enabled = False
    v['start_button'].enabled = True

''' Act on a button pressure '''
def button_tapped(sender):
    match sender.title:
        case '🏁':
            clock.lesson_good = 0
            clock.lesson_error = 0
            clock.lesson_count = 0
            v['score_label'].text = str(clock.lesson_good) + ' - ' + str(clock.lesson_error)  
            v['reset_button'].alpha = 0 
            v['start_button'].alpha = 1
            v['result_label'].text = ''
            
        case '🎲':
            label_result = sender.superview['text_label']
            clock.enabled = True
            v['start_button'].enabled = False
            v['result_label'].text = ''
            mode = v['lesson_segmentedcontrol'].selected_index
            match mode:
                case 0:
                    label_result.text = mode_hours()
                case 1:
                    label_result.text = mode_half_hours()
                case 2:
                    label_result.text = mode_quarter_hours()
                case 3:
                    label_result.text = mode_five_minutes()
            if (v['speech_button'].title == '🔈'):
                speech.say(label_result.text, 'nl_NL')
                finish_speaking()
        case '🔈':
            v['speech_button'].title = '🔇'
        case '🔇':
            v['speech_button'].title = '🔈' 


def finish_speaking():
    # Block until speech synthesis has finished
    while speech.is_speaking():
        time.sleep(0.1)


if __name__ == '__main__':
    v = ui.load_view('clock_ui')
    v.name = 'Learning Clock'
    v.border_color = '#2060e0'
    v.border_width = 0
    v['score_label'].text_color = CONST_TEXTCOLOR    
    v['reset_button'].alpha = 0
    
    
    clock = Clock()
    clock.on_change = check_result
    v['score_label'].text = str(clock.lesson_good) + ' - ' + str(clock.lesson_error) 
    
    frame = v['clock_view'].frame
    
    s = SceneView()
    s.x = 0
    s.y = 0
    s.width = frame.w
    s.height = frame.h
    s.scene = clock
    s.flex = 'LRB'
    
    v['clock_view'].add_subview(s)
    v.present('full_screen')
    tell_time = TellTime()
    tell_time.set_language('de_DE')



