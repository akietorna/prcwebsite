from flask import Flask,render_template



app = Flask(__name__)

app.config['DEBUG'] = True
app.debug = True

@app.route('/admin')
def tried():
    


if __name__=="__main__":
    app.run(debug=True)