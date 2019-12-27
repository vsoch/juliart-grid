#!/usr/bin/env python3

# I wanted to take a shot at generating a grid of Julia Sets, so I added:
#
# 1. a parameter to set the components of c (a and b) and generate an image,
# 2. an ability to write text on an image to keep track
#
# This basically walks through an animation generation, but saves intermediate
# png files, and allows us to change the text for each frame.

from juliart.main import JuliaSet

import json
import os
import sys

## Set parameters
# Set parameters intending to make more, smaller images
fontsize = 16
iterations = 200
resolution = 250
zoom = 1.8

# Let's generate a range of values for ca and cb that both span [-1, 1]
# Since we do this, we don't need to set frames
range_a = [x * 0.1 for x in range(-10, 10)]
range_b = [x * 0.1 for x in range(-10, 10)]
zooms = [zoom] * len(range_a)  # constant

# Use JuliaSet to generate a random color bias
juliaset = JuliaSet()
colorbias = juliaset.colorbias
glow = juliaset.glow

# plop images into images folder here
if not os.path.exists("images"):
    os.mkdir("images")

# Keep list of images, we will add them in reverse to generate the animation
images = []

# Generate the images, naming based on their ca and cb coordinates
for i, ca in enumerate(range_a):
    for cb in range_b:
        print("Generating for ca: %8.2f and cb: %8.2f" % (ca, cb))
        juliaset = JuliaSet(
            resolution=resolution, iterations=iterations, quiet=True, ca=ca, cb=cb
        )

        # Make sure we use consistent color
        juliaset.colorbias = colorbias
        juliaset.glow = glow
        juliaset.generate_image(zoom=zooms[i])

        # Add text for the coordinate (default fontsize is 16, xy coords are 10,10)
        juliaset.write_text("[ca=%3.2f][cb=%3.2f]" % (ca, cb))

        # Write image file based on ca and cb coordinates
        pngfile = os.path.join("images", "ca_%3.2f_cb_%3.2f.png" % (ca, cb))
        images.append(pngfile)
        juliaset.save_image(pngfile)

# Read in basic template
with open("template.html", "r") as filey:
    template = filey.read()

# Replace repository name
template = template.replace("{{REPO}}", "https://github.com/vsoch/juliart-grid")

# Generate data for images
imagedata = []
inputjson = {"bgcolor": "white"}

for i, ca in enumerate(range_a):
    for cb in range_b:

        # Since the values go from -1 to 1, we need x and y coords to be translated and scaled
        pngfile = os.path.join("images", "ca_%3.2f_cb_%3.2f.png" % (ca, cb))
        imagedata.append(
            {
                "y": (cb * 100) + 100,
                "x": (ca * 100) + 100,
                "zoom": zoom,
                "iters": iterations,
                "png": pngfile,
                "ca": "%3.2f" % ca,
                "cb": "%3.2f" % ca,
            }
        )

inputjson["image"] = imagedata

# Write in data
template = template.replace("{{DATA}}", json.dumps(inputjson, indent=4))

# Generate a simple index.html file to render (you can edit later to add style, etc.)
with open("index.html", "w") as filey:
    filey.writelines(template)


# Last step, to save an animation we need imageio
try:
    import imageio

    outfile = "juliaset_grid.gif"
    with imageio.get_writer(outfile, mode="I") as writer:
        for pngfile in images:
            writer.append_data(imageio.imread(pngfile))
except:
    print("Skipping animation, imageio is required.")
