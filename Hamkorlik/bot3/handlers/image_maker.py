import os
from PIL import Image,ImageFilter

def image_making():

    logo = 'handlers/post_media/logo.png'
    info = 'handlers/post_media/info.png'

    logo = Image.open(logo, 'r')
    info = Image.open(info, 'r')

    background_image = 'handlers/post_media/anime.jpg'

    original_image = Image.open(background_image)

    new_width = 1920
    new_height = 1080

    scaled_image = original_image.resize((new_width, new_height))
    scaled_image.save('handlers/post_media/anime.jpg')

    bg = Image.open(background_image, 'r')
    bg = bg.filter(ImageFilter.BoxBlur(4))
    bg.save('handlers/post_media/blured.jpg')
    bg = Image.open("handlers/post_media/blured.jpg", 'r')

    text_img = Image.new('RGB', (1920,1080), (0, 0, 0))
    text_img.paste(bg, (0,0))
    text_img.paste(logo, (650,270), mask=logo)
    text_img.paste(info, (0,900), mask=info)
    text_img.save("handlers/post_media/output.jpg")

    os.remove("handlers/post_media/blured.jpg")
    os.remove("handlers/post_media/anime.jpg")

    return "handlers/post_media/output.jpg"
