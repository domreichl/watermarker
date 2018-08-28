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
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        Label(self, text="1. Images:").grid(row=1, column=0, sticky=W)
        self.buttonOpen = Button(self, text="Open", command=self.load_images)
        self.buttonOpen.grid(row=2, column=0, sticky=W)

        Label(self, text="2. Text:").grid(row=3, column=0, sticky=W)
        self.entryText = Entry(self, width=50)
        self.entryText.grid(row=4, column=0, columnspan=2, sticky=W)

        Label(self, text="3. Color:").grid(row=5, column=0, sticky=W)
        self.buttonColor = Button(self, text="Choose", state=DISABLED, command=self.set_color)
        self.buttonColor.grid(row=6, column=0, sticky=W)

        Label(self, text="4. Transparency (.png files only):").grid(row=7, column=0, sticky=W)
        self.transparency = IntVar()
        self.scaleTransparency = Scale(self, variable=self.transparency, from_=0, to=255, length=300, tickinterval=50, orient="horizontal")
        self.scaleTransparency.grid(row=8, column=0, columnspan=2, sticky=W)

        Label(self, text="5. Alignment:").grid(row=9, column=0, sticky=W)
        alignment = [("top", 1), ("center", 2), ("bottom", 3)]
        self.align = IntVar()
        x = 0
        for mode, modeNum in alignment:
            Radiobutton(self, text=mode, variable=self.align, value=modeNum).grid(row=10+x, column=0, sticky=W)
            x += 1

        Label(self, text="6. Font:").grid(row=13, column=0, sticky=W)
        fonts = ["arial", "calibri", "comic", "impact", "tahoma", "times", "verdana"]
        self.listFonts = Listbox(self, height=len(fonts), activestyle=NONE)
        self.listFonts.grid(row=14, column=0, sticky=W)
        for font in fonts:
            self.listFonts.insert(END, font.title())

        Label(self, text="7. Size (small to large):").grid(row=15, column=0, sticky=W)
        self.size = DoubleVar()
        self.scaleSize = Scale(self, variable=self.size, from_=1, to=10, length=300, tickinterval=1, orient="horizontal")
        self.scaleSize.grid(row=16, column=0, columnspan=2, sticky=W)

        Label(self, text="8. Output Folder:").grid(row=17, column=0, sticky=W)
        self.folder = ""
        self.buttonFolder = Button(self, text="Set", state=DISABLED, command=self.choose_folder)
        self.buttonFolder.grid(row=18, column=0, sticky=W)

        Label(self, text="9. Add Watermark:").grid(row=19, column=0, sticky=W)
        self.buttonStart = Button(self, text="Start", state=DISABLED, command=self.add_watermarks)
        self.buttonStart.grid(row=20, column=0, sticky=W)

        Button(self, text="Reset", command=self.reset).grid(row=21, column=2)

    # function for click on buttonOpen
    def load_images(self):
        self.imagefiles = filedialog.askopenfilenames(title = "Select Picture(s)", filetypes = (("PNG files","*.png"), ("JPEG files","*.jpg")))
        filenames = []
        for i in self.imagefiles:
            filenames.append(os.path.basename(i))
            if i[-4:] not in (".png", ".jpg"):
                return messagebox.showerror("Error", "File must be PNG or JPG.")
        try:
            self.showFiles.destroy()
        except AttributeError:
            pass
        self.showFiles = Label(self, text=filenames)
        self.showFiles.grid(row=2, column=1, sticky=E)
        self.buttonColor.config(state=NORMAL)
        return self.imagefiles

    # function for click on buttonColor
    def set_color(self):
        (triple, hexstr) = colorchooser.askcolor()
        self.color = hexstr
        try:
            self.showColor.destroy()
        except AttributeError:
            pass
        self.showColor = Label(self, text="Color: " + str(self.color))
        self.showColor.grid(row=6, column=1, sticky=E)
        self.buttonFolder.config(state=NORMAL)
        return self.color

    # function for click on buttonFolder
    def choose_folder(self):
        self.folder = filedialog.askdirectory()
        if os.path.abspath(self.folder) == os.path.abspath(os.path.dirname(self.imagefiles[0])):
            messagebox.showwarning("Warning", "Original files will be overwritten.")
        try:
            self.showFolder.destroy()
        except AttributeError:
            pass
        self.showFolder = Label(self, text=self.folder)
        self.showFolder.grid(row=18, column=1, sticky=E)
        self.buttonStart.config(state=NORMAL)
        return self.folder

    # function for click on buttonStart
    def add_watermarks(self):
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
            # create objects
            image = Image.open(img)
            watermark = ImageDraw.Draw(image)

            # adjust font width to image width
            fontSize = 1
            font = ImageFont.truetype(fontStyle, fontSize)
            while watermark.textsize(text, font)[0] < self.scaleSize.get()*0.08*image.size[0]:
                fontSize += 1
                font = ImageFont.truetype(fontStyle, fontSize)

            # align font placement with image
            img_width, img_height = image.size
            txt_width, txt_height = watermark.textsize(text, font)
            coordinates = self.calc_alignment(img_width, img_height, txt_width, txt_height)

            # create new image (with alpha channel for .png)
            if os.path.splitext(img)[1] == ".jpg":
                watermark.text(coordinates, text, fill=color, font=font)
            elif os.path.splitext(img)[1] == ".png":
                if transparency == 0:
                    messagebox.showwarning("Warning", "Text transparency is 0.")
                image.convert("RGBA")
                canvas = Image.new("RGBA", image.size)
                watermark = ImageDraw.Draw(canvas)
                watermark.text(coordinates, text, fill=color, font=font)
                image = Image.alpha_composite(image, canvas)
            image.save(os.path.join(self.folder, os.path.basename(img)))
        
        Label(self, text="Watermark added.").grid(row=20, column=1)
        Button(self, text="Done", command=root.destroy).grid(row=21, column=1)

    # calculate relative position for text on picture
    def calc_alignment(self, img_width, img_height, txt_width, txt_height):
        mode = self.align.get()
        coordinates = (0, 0)
        if mode == 1: # top
            coordinates = ((img_width/2)-(txt_width/2), img_height*0.04)
        elif mode == 2: # center
            coordinates = ((img_width/2)-(txt_width/2), (img_height/2)-(txt_height/2))
        elif mode == 3: # bottom
            coordinates = ((img_width/2)-(txt_width/2), (img_height*0.96)-txt_height)
        return coordinates

    # function for click on reset button
    def reset(self):
        python = sys.executable
        os.execl(python, python, * sys.argv)

root = Tk()
app = Watermarker(master=root)
app.master.title("Dom's Watermarker")
app.mainloop()
