from flask import render_template, Flask
import wtforms
from flask import request

app = Flask(__name__)



class RegistrationForm(wtforms.Form):
    username = wtforms.StringField('Username', [wtforms.validators.Length(min=4, max=25)])


@app.route('/', methods=['GET', 'POST'])
def t():
    return render_template('mng.html', form = RegistrationForm(request.form))

app.run()