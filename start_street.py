from classes.classes_sb import street_beat
import json



#config = json.load(open('cfg.json'))

#webhooks = "webhook"
url = 'https://street-beat.ru/cat/krossovki/?q=Air+Jordan+1&regular_search=Y'
monitor = street_beat(webhooks,url)
monitor.start()
