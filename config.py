import os

if os.path.exists('localtesting.py') == True:
	SECRET_KEY = "NotARealKey!"

else:
	try:
		SECRET_KEY = os.environ['SECRET_KEY']
	except KeyError:
		SECRET_KEY = "NotARealKey!"

CSRF_ENABLED = True