#!/usr/bin/env python
"""
    Image Placeholder Server
    By Arielle B Cruz <http://www.abcruz.com> <arielle.cruz@gmail.com>
    Dedicated to the Public Domain on January 2013.
    
    Description:
        Inspired by http://placehold.it. Generates placeholder images for web
        pages in development but does not require an active Internet connection.
        
        Requires the Python Imaging Library.
    
    Usage:
        Run this script in a terminal.
        
        Point browser or link HTML to http://localhost:5000/(width)x(height)
              or http://localhost:5000/(width)x(height)/(colour hex code)
    
    Credits:
        http://lost-theory.org/python/dynamicimg.html
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import Image, ImageDraw
import cStringIO

server_port = 5001
default_size = (320, 100)
default_colour = "FFFFFF"

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Check the requested path.
        self.check_path()
        # Create the image.
        self.create_image()
        # Start responding.
        self.respond()
    
    def check_path(self):
        """Checks the path for the image dimensions and an optional colour."""
        p = self.path.split("/")[1:]
        self.img_colour = default_colour
        self.img_size = default_size
        # Get the colour, that's required any way.
        wh = p[0].split("x")
        if len(wh) == 2:
            if wh[0].isdigit() and wh[1].isdigit():
                self.img_size = (int(wh[0]), int(wh[1]))
        # If we have a second component, that should be the colour.
        if len(p) == 2:
            c = [x for x in p[1] if x in "0123456789aAbBcCdDeEfF"]
            if len(c) == 6 or len(c) == 3:
                self.img_colour = "".join(c)
    
    def create_image(self):
        """Creates the image that the server is going to send out."""
        # we want a darker color for the coordinate text. So we subtract coord_color from self.img_colour
        coord_subtract = int("0x44",16) # for each color (R, G & B), modify 33 to any hex as liked.
        # slice the #RRGGBB into RR, GG, BB
        coord_color_r = int(self.img_colour[:2],16)
        coord_color_g = int(self.img_colour[2:4],16)
        coord_color_b = int(self.img_colour[4:6],16)
        
        # and because subtracting e.g. 0x3 from 0x1 won't be 0x00 but 0xDD, we need these if-lines aswell...
        if coord_color_r > coord_subtract:
            coord_color_r = hex(coord_color_r -coord_subtract).replace("0x","")
        else:
            coord_color_r = "00";
        if coord_color_g > coord_subtract:
            coord_color_g = hex(coord_color_g -coord_subtract).replace("0x","")
        else:
            coord_color_g = "00";
        if coord_color_b > coord_subtract:
            coord_color_b = hex(coord_color_b -coord_subtract).replace("0x","")
        else:
            coord_color_b = "00";

        # coord_color contains now the darker color.
        coord_color = "#" + coord_color_r + coord_color_g + coord_color_b

        # The image to be sent out.
        self.img = Image.new("RGB", self.img_size,"#" + self.img_colour)
        # Add the dimensions of the requested image to the image itself.
        img = Image.new("RGB", (10, 10), coord_color)
        draw = ImageDraw.Draw(img)
        coord_string = str(self.img_size[0]) + " x " + str(self.img_size[1])
        txw, txh = draw.textsize(coord_string)
        new_img = img.resize((txw + 10, txh + 10))
        draw = ImageDraw.Draw(new_img)

        draw.text((5, 5), coord_string, fill="#"+self.img_colour)
        self.img.paste(new_img, (self.img_size[0]/2-(txw/2)-5,self.img_size[1]/2-txh))
    
    def respond(self):
        """Sends the response."""
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        # Save the image to a temporary file-like object.
        f = cStringIO.StringIO()
        self.img.save(f, "PNG")
        f.seek(0)
        self.wfile.write(f.read())


if __name__ == "__main__":
    
    try:
        server = HTTPServer(("", server_port), MyHandler)
        print "Simple HTTP server started on port %s." % server_port
        server.serve_forever()
    
    except KeyboardInterrupt:
        print "\nInterrupted. Goodbye."
        server.socket.close()
