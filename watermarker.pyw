#! python3
# watermarker_grid.pyw by Dom Reichl
# adds a text watermark to images
# requires PIL: pip install Pillow

import os, sys
from tkinter import *
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageFont

class Watermarker(Frame):
    def __init__(self, master=None):
        ''' Initializes master frame with grid geometry and loads widgets '''
        
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        '''
        Adds 4 buttons, 1 text field, 2 scales, 1 set of 3 radio buttons, and 1 list box,
        all with text labels, as well as 1 reset button without a label to the grid frame.
        '''
        
        # Button for loading images
        Label(self, text="1. Images:").grid(row=1, column=0, sticky=W)
        self.buttonOpen = Button(self, text="Open", command=self.load_images)
        self.buttonOpen.grid(row=2, column=0, sticky=W)

        # Field for entering a custom watermark text
        Label(self, text="2. Text:").grid(row=3, column=0, sticky=W)
        self.entryText = Entry(self, width=50)
        self.entryText.grid(row=4, column=0, columnspan=2, sticky=W)

        # Button for choosing a text color
        Label(self, text="3. Color:").grid(row=5, column=0, sticky=W)
        self.buttonColor = Button(self, text="Choose", state=DISABLED, command=self.set_color)
        self.buttonColor.grid(row=6, column=0, sticky=W)

        # Scale for choosing transparency
        Label(self, text="4. Transparency (.png files only):").grid(row=7, column=0, sticky=W)
        self.transparency = IntVar()
        self.scaleTransparency = Scale(self, variable=self.transparency, from_=0, to=255, length=300, tickinterval=50, orient="horizontal")
        self.scaleTransparency.grid(row=8, column=0, columnspan=2, sticky=W)

        # Three radio buttons for choosing text position (top, center, or bottom)
        Label(self, text="5. Alignment:").grid(row=9, column=0, sticky=W)
        alignment = [("top", 1), ("center", 2), ("bottom", 3)]
        self.align = IntVar()
        x = 0
        for mode, modeNum in alignment:
            Radiobutton(self, text=mode, variable=self.align, value=modeNum).grid(row=10+x, column=0, sticky=W)
            x += 1

        # Listbox for choosing one of seven fonts
        Label(self, text="6. Font:").grid(row=13, column=0, sticky=W)
        fonts = ["arial", "calibri", "comic", "impact", "tahoma", "times", "verdana"]
        self.listFonts = Listbox(self, height=len(fonts), activestyle=NONE)
        self.listFonts.grid(row=14, column=0, sticky=W)
        for font in fonts:
            self.listFonts.insert(END, font.title())

        # Scale for choosing text size, which will be calculated relative to image size
        Label(self, text="7. Size (small to large):").grid(row=15, column=0, sticky=W)
        self.size = DoubleVar()
        self.scaleSize = Scale(self, variable=self.size, from_=1, to=10, length=300, tickinterval=1, orient="horizontal")
        self.scaleSize.grid(row=16, column=0, columnspan=2, sticky=W)

        # Button for setting output dictionary
        Label(self, text="8. Output Folder:").grid(row=17, column=0, sticky=W)
        self.folder = ""
        self.buttonFolder = Button(self, text="Set", state=DISABLED, command=self.choose_folder)
        self.buttonFolder.grid(row=18, column=0, sticky=W)

        # Button for calling the function that adds the watermark
        Label(self, text="9. Add Watermark:").grid(row=19, column=0, sticky=W)
        self.buttonStart = Button(self, text="Start", state=DISABLED, command=self.add_watermarks)
        self.buttonStart.grid(row=20, column=0, sticky=W)

        # Button for resetting the entire frame by reloading the program
        Button(self, text="Reset", command=self.reset).grid(row=21, column=2)

    def load_images(self):
        '''
        Called by click on buttonOpen.
        Opens file dialog for selecting either PNG or JPG files.
        Displays error message if another file type is selected.
        Creates label widget that displays the filenames in the frame.
        Enables click on buttonColor, which should be the user's second next step.
        Returns list of paths of selected files.
        '''
        
        self.imagefiles = filedialog.askopenfilenames(title = "Select Picture(s)", filetypes = (("PNG files","*.png"), ("JPG files","*.jpg")))
        filenames = []
        for i in self.imagefiles:
            filenames.append(os.path.basename(i)) # builds list of filenames
            if i[-4:] not in (".png", ".jpg"): # checks if file type is correct
                return messagebox.showerror("Error", "File must be PNG or JPG.")
        try:
            self.showFiles.destroy() # removes label if one already exists
        except AttributeError:
            pass # does nothing if user hasn't reselected the files
        self.showFiles = Label(self, text=filenames) # creates label for filenames
        self.showFiles.grid(row=2, column=1, sticky=E) # puts label into grid frame
        self.buttonColor.config(state=NORMAL) # enables click on second button
        return self.imagefiles

    def set_color(self):
        '''
        Called by click on buttonColor.
        Opens color dialog for selecting a color.
        Creates label widget that displays its hex string in the frame.
        Enables click on buttonFolder, which should be the user's second last step.
        Returns color as a hex string.
        '''
        
        (triple, hexstr) = colorchooser.askcolor()
        self.color = hexstr
        try:
            self.showColor.destroy() # removes label if one already exists
        except AttributeError:
            pass # does nothing if user hasn't reselected the color
        self.showColor = Label(self, text="Color: " + str(self.color)) # creates label for color
        self.showColor.grid(row=6, column=1, sticky=E) # puts label into grid frame
        self.buttonFolder.config(state=NORMAL) # enables click on third button
        return self.color

    def choose_folder(self):
        '''
        Called by click on buttonFolder.
        Opens dictionary dialog for selecting an output folder.
        Displayes warning message if input and output folder are the same.
        Creates label widget that displays the output directory path in the frame.
        Enables click on buttonStart, which may be the user's final step.
        Returns output directory path.
        '''
        
        self.folder = filedialog.askdirectory()
        if os.path.abspath(self.folder) == os.path.abspath(os.path.dirname(self.imagefiles[0])):
            messagebox.showwarning("Warning", "Original files will be overwritten.")
        try:
            self.showFolder.destroy() # removes label if one already exists
        except AttributeError:
            pass # does nothing if user hasn't reselected the directory
        self.showFolder = Label(self, text=self.folder) # creates label for output directory
        self.showFolder.grid(row=18, column=1, sticky=E) # puts label into grid frame
        self.buttonStart.config(state=NORMAL) # enables click on last disabled button
        return self.folder

    def add_watermarks(self):
        '''
        Called by click on buttonStart.
        Gets text and font unless they weren't entered and selected, resp.
        Process images by putting a watermark on each.
        Create label 'Watermark added.' to display finished process.
        Create button 'Done' for closing the program.
        '''
        
        # transform hex color into RGBA
        color = self.color.lstrip("#")
        transparency = self.scaleTransparency.get()
        rgb = [int(color[i:i+2], 16) for i in (0,2,4)]
        color = (rgb[0], rgb[1], rgb[2], transparency)

        # get text & font
        if self.entryText.get() == "":
            messagebox.showerror("Error", "Please enter text.")
            return
        else:
            text = self.entryText.get()
        if self.listFonts.curselection() == ():
            messagebox.showerror("Error", "Please select font.")
            return
        else:
            fontStyle = self.listFonts.get(self.listFonts.curselection()).lower() + ".ttf"

        # process image by image
        for img in self.imagefiles:
            # create key objects
            image = Image.open(img)
            watermark = ImageDraw.Draw(image)

            # adjust font width to image width
            fontSize = 1 # set font size to minimum
            font = ImageFont.truetype(fontStyle, fontSize) # create font object
            while watermark.textsize(text, font)[0] < self.scaleSize.get()*0.08*image.size[0]:
                fontSize += 1 # scale up font width until it's 8-80%, depending on user's choice, of image width
                font = ImageFont.truetype(fontStyle, fontSize) # adjust font object

            # align font placement with image
            img_width, img_height = image.size
            txt_width, txt_height = watermark.textsize(text, font)
            coordinates = self.calc_alignment(img_width, img_height, txt_width, txt_height)

            # create new image
            if os.path.splitext(img)[1] == ".jpg": # JPG without alpha channel
                watermark.text(coordinates, text, fill=color, font=font)
            elif os.path.splitext(img)[1] == ".png": # PNG with alpha channel
                if transparency == 0:
                    messagebox.showwarning("Warning", "Text transparency is 0.")
                image.convert("RGBA") # convert image object into RGBA
                canvas = Image.new("RGBA", image.size) # create additional RGBA image object
                watermark = ImageDraw.Draw(canvas) # create new draw object
                watermark.text(coordinates, text, fill=color, font=font) # draw watermark on new image object
                image = Image.alpha_composite(image, canvas) # overlap both image objects with alpha channel
            image.save(os.path.join(self.folder, os.path.basename(img))) # save image in output folder
        
        # create two new widgets
        Label(self, text="Watermark added.").grid(row=20, column=1)
        Button(self, text="Done", command=root.destroy).grid(row=21, column=1)

    def calc_alignment(self, img_width, img_height, txt_width, txt_height):
        '''
        Called by function 'add_watermarks'.
        Calculates the custom text's relative position on the picture.
        Returns coordinates for text placement.
        '''
        
        mode = self.align.get() # get user's choice of text position
        coordinates = (0, 0) # initialize coordinates
        if mode == 1: # text on top
            coordinates = ((img_width/2)-(txt_width/2), img_height*0.04)
        elif mode == 2: # text in center
            coordinates = ((img_width/2)-(txt_width/2), (img_height/2)-(txt_height/2))
        elif mode == 3: # text on bottom
            coordinates = ((img_width/2)-(txt_width/2), (img_height*0.96)-txt_height)
        return coordinates

    def reset(self):
        '''
        Called by click on reset button.
        Resets the master frame by reloading the program.
        '''
        
        python = sys.executable
        os.execl(python, python, * sys.argv)

root = Tk()
app = Watermarker(master=root)
app.master.title("Dom's Watermarker")
app.mainloop()
