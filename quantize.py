from PIL import Image

def dither(img):
    def customConvert(silf, palette, dither=False):
        ''' Convert an RGB or L mode image to use a given P image's palette.
            PIL.Image.quantize() forces dither = 1. 
            This custom quantize function will force it to 0.
            https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering
        '''

        silf.load()

        # use palette from reference image made below
        palette.load()
        im = silf.im.convert("P", 1 if dither else 0, palette.im)
        # the 0 above means turn OFF dithering making solid colors
        return silf._new(im)

    palette = [202,227,255,
        255,255,255,
        255,255,255,
        228,228,228,
        196,196,196,
        136,136,136,
        78,78,78,
        0,0,0,
        244,179,174,
        255,167,209,
        255,84,178,
        255,101,101,
        229,0,0,
        154,0,0,
        254,164,96,
        229,
        149,0,160,
        106,66,96,
        64,40,245,
        223,176,255,
        248,137,229,
        217,0,148,
        224,68,2,
        190,1,104,
        131,56,0,
        101,19,202,
        227,255,0,
        211,221,0,
        131,199,
        0,0,234,
        25,25,115,
        207,110,228,
        130,0,128] + [0,] * (768 - 3 * 96)
    # a palette image to use for quant
    paletteImage = Image.new('P', (1, 1), 0)
    paletteImage.putpalette(palette)

    # convert it using our palette image
    imageCustomConvert = customConvert(img, paletteImage, dither=True).convert('RGBA')
    return imageCustomConvert


