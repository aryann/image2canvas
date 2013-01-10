#!/usr/bin/env python
"""A program that generates grayscale JavaScript canvas code for an image.

You must have the Python Imaging Library (PIL) installed before being
able to use this:

    sudo pip install PIL

This program is known to work for JPEG images, but could potentially
work for other formats too!

Usage:

    ./image2canvas.py <path-to-image>

The generated code is written to standard out.

Note that this utility is probably not very useful. The generated
HTML/JavaScript code can be hefty in size (e.g., 25 KB JPEG -> 486
KB!) since no effort was made to compress the data and the bitwise
operations can be a performance drain.
"""

__author__ = 'Aryan Naraghi (aryan.naraghi@gmail.com)'

import Image
import ImageOps
import string
import sys
import textwrap


_TEMPLATE = textwrap.dedent("""\
    <!doctype html>
    <html>
      <body>
        <canvas id="c"></canvas>
        <script type="text/javascript">
          (function() {
            var canvas = document.getElementById("c");
            var context = canvas.getContext("2d");
            context.canvas.width = $width;
            context.canvas.height = $height;
            var canvasData = context.getImageData(0, 0, canvas.width, canvas.height);

            var Point = function(x, y) {
              this.x = x;
              this.y = y;
            }

            var setPixel = function(pixel, grayscale) {
              var index = (pixel.x + pixel.y * canvas.width) * 4;
              canvasData.data[index] = grayscale;
              canvasData.data[index + 1] = grayscale;
              canvasData.data[index + 2] = grayscale;
              canvasData.data[index + 3] = 255;
            }

            var packedGrayscales = [$grayscales];

            var mask = (1 << 8) - 1;
            for (var x = 0; x < canvas.width; x++) {
              for (var y = 0; y < canvas.height; y++) {
                var pixel = x + y * canvas.width;
                var bucket = Math.floor(pixel / 4);
                var grayscale = (packedGrayscales[bucket] >> (3 - pixel % 4) * 8) & mask;
                setPixel(new Point(x, y), grayscale);
              }
            }
            context.putImageData(canvasData, 0, 0);
          })();
        </script>
      </body>
    </html>
    """)


def main(argv):
    if len(argv) != 2:
        raise ValueError(
            'Expected path to image. Usage: ./{0} <path-to-image>'.format(
                argv[0]))

    filename = argv[1]
    img = ImageOps.grayscale(Image.open(filename))

    packed_grayscales = []
    data = img.getdata()
    for i in xrange(0, len(data), 4):
        packed_int = 0
        for j in xrange(4):
            if i + j >= len(data):
                break
            packed_int <<= 8
            packed_int += data[i + j]
        packed_grayscales.append(packed_int)

    width, height = img.size
    print string.Template(_TEMPLATE).substitute(
        width=width,
        height=height,
        grayscales=', '.join(str(p) for p in packed_grayscales))


if __name__ == '__main__':
    main(sys.argv)
