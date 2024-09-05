from flask import Flask, render_template, request, redirect, url_for
import utilv2
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

def url2qr(url, filename="qr.png"):
    """
    Convert a URL to a QR code and save it as an image file in the QR folder.
    
    :param url: The URL to encode in the QR code
    :param filename: The filename to save the QR code image (default: "qr.png")
    :return: None
    """
    # Create a QR code instance
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    
    # Add the URL data
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Ensure the QR folder exists
    os.makedirs("static/QR", exist_ok=True)
    
    # Save the image in the QR folder
    full_path = os.path.join("static/QR", filename)
    # print(full_path)
    img.save(full_path)
    
    return [full_path, os.path.join("QR", filename)]

def nameSGP(name, baseImg, font="nourd", filename="qrbyname.png"):
    font_preset = {
        "nunito": {
            "x": 196,
            "y": 723,
            "RGB": (54, 56, 59),
            "font_size": 38,
        },
        "ttnorms": {
            "x": 255,
            "y": 703,
            "RGB": (0, 0, 0),
            "font_size": 33,
        },
        "nourd": {
            "x": 0,
            "y": 450,
            "RGB": (116, 79, 65),
            "font_size": 39,
        }
    }
    # Open the base image
    font_path = os.path.join("font", f"{font}.ttf") if font in ["nourd", "nunito"] else os.path.join("font", f"{font}.otf")
    base_path = os.path.join("sgp", "nt", f"{baseImg}.png")
    img = Image.open(base_path)

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    # Get font settings from preset
    x = font_preset[font]["x"]
    y = font_preset[font]["y"]
    fontsize = font_preset[font]["font_size"]
    rgb = font_preset[font]["RGB"]

    # Load the specified font
    try:
        font_obj = ImageFont.truetype(font_path, int(fontsize))
    except IOError:
        print(f"Failed to load font: {font_path}")
        font_obj = ImageFont.load_default()
        fontsize = 12  # Default size if font loading fails

    # Add text to the image
    text = f"Dear {name}"
    
    if font == "nourd":
        # Calculate the width of the text
        text_width, _ = draw.textsize(text, font=font_obj)
        # Calculate the center position
        x = ( (img.width - text_width) // 2 ) - 5
    
    draw.text((x, y), text, font=font_obj, fill=rgb, size=int(fontsize))  # Text with specified color and size

    # Save the modified image
    img.save(filename)
    print(f"Image saved as {filename}")

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/util/qrgen', methods=['GET', 'POST'])
def qrgen():
    if request.method == 'POST':
        form_data = {
            'fujiutil_name': request.form.get('fujiutil_name'),
            'fujiutil_format': request.form.get('fujiutil_format')
        }
        
        font_preset = {
            "1": "nunito",
            "2": "ttnorms",
            "3": "nourd"
        }

        nameSGP(form_data['fujiutil_name'], int(form_data['fujiutil_format']), font_preset[str(form_data['fujiutil_format'])], f"static/Outsgp/{form_data['fujiutil_name'].replace(' ', '')}.png")
        return redirect(url_for('sgnqr', url=f"{request.host_url}util/sgp?view={form_data['fujiutil_name'].replace(' ', '')}.png"))

    project = request.args.get('project')
    if project == 'sgp':
        return render_template('qrgen_sgp.html')
    else:
        return render_template('qrgen.html')
    
@app.route('/util/sgp/qr')
def sgnqr():
    url = request.args.get('url')
    
    try:
        fn = url.replace(f"{request.host_url}util/sgp?view=","")
    except Exception as e:
        print(e)

    try:
        res = url2qr(f"{request.host_url}util/sgp?view="+fn, filename=fn)
    except Exception as e:
        res = e
    print(fn)
    print(res)
    res2 = str(res[1]).replace("/static", "").replace("\\", "/")
    return render_template('sgpQR.html', path=res2)

@app.route('/util/sgp')
def sgp():
    fn = request.args.get('view')
    return render_template('sgp.html', filename=fn)


@app.route('/utilv2')
def utilv2():
    return render_template('utilv2.html')

@app.route('/api/v1/generate/qr/sgp', methods=['POST'])
def api_v1_generate_qr_sgp():
    posted_data = request.get_json()
    name = posted_data.get('name')
    formats = posted_data.get('format')
    font = posted_data.get('font')
    try:
        fn = f"Outsgp/{name}.png"
        utilv2.nameSGP(name, formats, font, filename=fn)
    except Exception as e:
        fn = f"Out/{name}_1.png"
        utilv2.nameSGP(name, formats, font, filename=fn)

    return {"status": "202 ", "filename": fn}


if __name__ == '__main__':
    app.run(debug=True)
