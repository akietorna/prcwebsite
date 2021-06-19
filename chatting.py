from flask import Flask,render_template,request
from datetime import datetime
import os
import pusher


def counselling():
    pusher_client = pusher.Pusher(
    app_id = '1204913',
    key = 'fb1f00da186d813ba11e',
    secret = 'a01992d2d0e0ff64a6bb',
    cluster = 'mt1',
    ssl = True
    )

    return pusher_client