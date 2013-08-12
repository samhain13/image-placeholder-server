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
default_colour = "#FFFFFF"

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
                self.img_colour = "#" + "".join(c)
    
    def create_image(self):
        """Creates the image that the server is going to send out."""
        # The image to be sent out.
        self.img = Image.new("RGB", self.img_size, self.img_colour)
        # Add the dimensions of the requested image to the image itself.
        img = Image.new("RGB", (10, 10), "#000000")
        draw = ImageDraw.Draw(img)
        txw, txh = draw.textsize(str(self.img_size))
        new_img = img.resize((txw + 10, txh + 10))
        draw = ImageDraw.Draw(new_img)
        draw.text((5, 5), str(self.img_size), fill="#CCCCCC")
        self.img.paste(new_img, (5, 5))
    
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
