from flask import Flask, render_template, request, make_response, Response
import datetime
import os


app = Flask(__name__)

def calculate_gst_exclusive(amount, gst_rate):
    gst_amount = round((amount * gst_rate) / 100, 2)
    total_amount = round(amount + gst_amount, 2)
    return gst_amount, total_amount

def calculate_gst_inclusive(amount, gst_rate):
    gst_amount = round(amount - (amount / (1 + gst_rate / 100)), 2)
    base_amount = round(amount - gst_amount, 2)
    return gst_amount, base_amount

@app.route('/', methods=['GET', 'POST'])
def index():
    base_amount = gst_amount = total_amount = None
    error = None
    if request.method == 'POST':
        amount = request.form['amount']
        gst_rate = request.form['gst_rate']
        gst_inclusive = request.form['gst_inclusive']

        try:
            amount = int(amount)
            gst_rate = int(gst_rate)
        except ValueError:
            error = "Please enter valid numbers"
            return render_template('index.html', error=error)

        if gst_inclusive == 'exclusive':
            gst_amount, total_amount = calculate_gst_exclusive(amount, gst_rate)
            base_amount = amount
        else:
            gst_amount, base_amount = calculate_gst_inclusive(amount, gst_rate)
            total_amount = amount

        resp = make_response(render_template('index.html', base_amount=base_amount, gst_amount=gst_amount, total_amount=total_amount, gst_rate=gst_rate, gst_inclusive=gst_inclusive))
        resp.set_cookie('base_amount', str(base_amount))
        resp.set_cookie('gst_amount', str(gst_amount))
        resp.set_cookie('total_amount', str(total_amount))
        return resp
    
    base_amount = request.cookies.get('base_amount')
    gst_amount = request.cookies.get('gst_amount')
    total_amount = request.cookies.get('total_amount')

    return render_template('index.html', base_amount=base_amount, gst_amount=gst_amount, total_amount=total_amount)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    ten_days_ago = (datetime.datetime.now() - datetime.timedelta(days=10)).date().isoformat()

    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and rule.endpoint != 'static':
            pages.append([rule.rule, ten_days_ago])

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = Response(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

