from library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation

from PIL import Image, ImageDraw, ImageFont

class screen:
    def __init__(self):
        self.lcd = LcdCommRevA(com_port="AUTO",
                               display_width=320,
                               display_height=480)
        self.lcd.Reset()
        self.lcd.InitializeComm()
        # Set orientation (screen starts in Portrait)
        self.orientation = Orientation.REVERSE_LANDSCAPE
        self.lcd.SetOrientation(orientation=self.orientation)
        self.current_background = ''
        self.time = ''
        self.date = ''

    def on(self):
        self.lcd.SetOrientation(orientation=self.orientation)
        self.lcd.ScreenOn()
        # Set brightness in % (warning: revision A display can get hot at high brightness!)
        self.lcd.SetBrightness(level=10)

    def off(self):
        self.lcd.Clear()
        self.lcd.ScreenOff()

    def setBackground(self, background_path):
        self.current_background = background_path

    def setTime(self, text, x, y, font, font_size, font_color,align='left'):
        self.time = text
        self.time_x = x
        self.time_y = y
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.align = align

    def setDate(self, text, x, y, font, font_size, font_color,align='left'):
        self.date = text
        self.date_x = x
        self.date_y = y
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.align = align

    def draw(self):
        if not self.current_background:
            return
        
        # Convert text to bitmap using PIL and display it
        # Provide the background image path to display text with transparent background

        if self.time:
            if isinstance(self.font_color, str):
                self.font_color = tuple(map(int, self.font_color.split(', ')))

            assert self.time_x <= self.lcd.get_width(), 'time X coordinate ' + str(self.time_x) + ' must be <= display width ' + str(
                self.lcd.get_width())
            assert self.time_y <= self.lcd.get_height(), 'time Y coordinate ' + str(self.time_y) + ' must be <= display height ' + str(
                self.lcd.get_height())
            assert len(self.time) > 0, 'time must not be empty'
            assert self.font_size > 0, "Font size must be > 0"

            # The time bitmap is created from provided background image : time with transparent background
            time_image = Image.open(self.current_background)

            # Get time bounding box
            font_image = ImageFont.truetype("./res/fonts/" + self.font, self.font_size)
            d = ImageDraw.Draw(time_image)
            left, top, time_width, time_height = d.textbbox((0, 0), self.time, font=font_image)
            # Draw text with specified color & font, remove left/top margins
            d.text((self.date_x - left, self.time_y - top), self.time, font=font_image, fill=self.font_color, align=self.align)

            if self.date:
                d = ImageDraw.Draw(time_image)
                left, top, time_width, time_height = d.textbbox((0, 0), self.date, font=font_image)
                # Draw text with specified color & font, remove left/top margins
                d.text((self.time_x - left, self.date_y - top), self.date, font=font_image, fill=self.font_color, align=self.align)

            image = time_image
        else:
            image = Image.open(self.current_background)

        self.lcd.DisplayPILImage(image, 0, 0, self.lcd.get_width(), self.lcd.get_height())

    def clean_stop(self):
        self.lcd.Clear()
        self.lcd.ScreenOff()

    def close(self):
        self.lcd.closeSerial()