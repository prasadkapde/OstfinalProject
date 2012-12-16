from flask import Flask
import settings
app = Flask('ostpk1094')
app.config.from_object('ostpk1094.settings')

import views
