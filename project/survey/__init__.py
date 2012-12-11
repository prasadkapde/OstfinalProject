from flask import Flask
import settings
app = Flask('survey')
app.config.from_object('survey.settings')

import views
