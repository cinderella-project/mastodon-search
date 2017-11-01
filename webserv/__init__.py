from flask import Flask, render_template, request
import utils

app = Flask(__name__)
app.jinja_env.add_extension("pyjade.ext.jinja.PyJadeExtension")

@app.route('/')
def index():
    return render_template("index.jade")
@app.route('/search')
def searchpage():
    m = (utils.search(request.args["q"].split(" ")))
    print(m)
    return render_template("search.jade", q=request.args["q"], toots=m)

app.run(port=3000)