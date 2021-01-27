import requests
from bs4 import BeautifulSoup as trxk
from threading import Thread
from selenium import webdriver
import time
import random
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
import json

class street_beat:
    def __init__(self,webhooks,url):
        self.webhooks = webhooks
        self.products = []
        self.latest_status = ""
        self.url = url

    def start(self):
        t = Thread(target=self.mntr)
        t.start()

    def link_checker(self):
        with open("sb_blacklist.txt", "r") as book:
            with open("sb_blacklist.txt", "a") as pen:
                read = book.read()
                if link not in read:
                    pen.write(link + '\n')
                    print("NEW LINK IN FILE")

    def mntr(self):
        with open('cfg.json') as f:
            templates = json.load(f)
        driver = webdriver.Chrome('webdriver": "*/*/*/*/chromedriver.exe')
        driver.set_window_size(1, 1)

        while True:
            try:
                driver.get(self.url)
                requiredHtml = driver.page_source
                soup = trxk(requiredHtml, 'html5lib')
                table = soup.findAll("a",class_='link link--no-color catalog-item__title ddl_product_link')
                for i in table:
                    link = "https://street-beat.ru" + i.get('href')
                    main_sizes = ''
                    low_sizes = ''
                    special = []
                    now = datetime.now()
                    driver.get(link) #цикловая
                    print(link+"\n["+str(now)+"]")
                    new_page = driver.page_source
                    soup = trxk(new_page, 'html5lib')
                    name = soup.find("h1",class_='product-heading').text.split("Арт.")[0].strip()
                    price = soup.find("div",class_='price--current').text
                    img = str(soup.find('div', attrs={'data-slick-index': '1'}).find('img').get('src')).replace('100_100_1','500_500_1')
                    #us = soup.findAll("ul",attrs={'class':'sizes__table hidden','data-size-type':'tab_us'})
                    us = soup.findAll("ul",attrs={'class':'sizes__table','data-size-type':'tab_us'})
                    full = us[0].findAll("li", attrs={"class": ""})
                    last = us[0].findAll("li", attrs={"class": "last"})

                    if full:#us = soup.findAll("ul", attrs={'class': 'sizes__table sizes__table--multi current', 'data-size-type': 'tab_us'})
                        for me in full:
                            pol = me.find("input", attrs={'name': 'size-us'})
                            text1 = pol['data-size']
                            for_atc1_1 = pol['data-prod-id'] #2190172 2190174
                            for_atc2_1 = pol['data-sku-id'] #https://pasichniy-private.com/pages/streetbeat?product={}&sku={}
                            atc = f'https://YOUR_URL/pages/streetbeat?product={for_atc1_1}&sku={for_atc2_1}'
                            main_sizes+=f'[{text1} [high] ]({atc})\n'
                            special.append(text1)
                        #print("[High size stock]")
                        if last:
                            for ot in last:
                                lop = ot.find("input", attrs={'name': 'size-us'})
                                text2 = lop['data-size']
                                for_atc1 = lop['data-prod-id']
                                for_atc2 = lop['data-sku-id']
                                atc = f'https://YOUR_URL/pages/streetbeat?product={for_atc1}&sku={for_atc2}'
                                main_sizes+=f'[{text2} [low] ]({atc})\n'
                                special.append(text2)
                            print("[Low size stock] & [High size stock]")
                        else:
                            print("[High size stock]")
                        status = True
                    else:
                        status = False
                        if last:
                            for o in last:
                                lopv2 = o.find("input", attrs={'name': 'size-us'})
                                text3 = lopv2['data-size']
                                for_atc1_2 = lopv2['data-prod-id']
                                for_atc2_2 = lopv2['data-sku-id']
                                atc = f'https://YOUR_URL/pages/streetbeat?product={for_atc1_2}&sku={for_atc2_2}'
                                low_sizes+=f'[{text3} [low] ]({atc})\n'
                                special.append(text3)
                            print("[Low size stock]")
                        else:
                            print("Sizes were not found")

                    if len(special) == 0:
                        status2 = 'OUT OF STOCK'
                        print("Oos")
                    else:
                        status2 = 'IN STOCK'

                    product = {'name': name, 'link': link, 'price': price, 'sizes': special, 'sizes1': main_sizes,'sizes2': low_sizes, 'img': img, 'status': status,"status2":status2}
                    buff_product = list([x for x in self.products if link in x.values()])
                    if len(buff_product) == 0:
                        self.products.append(product)
                        self.send_to_discord(product)
                    else:
                        if buff_product[0]['status2'] != product['status2']:
                            self.products.remove(buff_product[0])
                            self.products.remove(buff_product[0])
                            self.products.append(product)
                            self.send_to_discord(product)
                        if buff_product[0]['sizes'] != product['sizes']:
                            self.products.remove(buff_product[0])
                            self.products.append(product)
                            self.send_to_discord(product)
            except Exception as fuck:
                print(fuck)

    def send_to_discord(self,product): #need to cut back, low speed
        webhook = DiscordWebhook(url=self.webhooks)
        if product['sizes1'] != '':
            embed = DiscordEmbed(title=product['name'] + " on streetbeat.ru", url=product['link'], color=2544107)#,timestamp='now'
            embed.set_thumbnail(url=product['img'])
            embed.add_embed_field(name='**Sizes**', value=product['sizes1'])#, inline=(product['sizes2'] != '')
            embed.add_embed_field(name='**Price**', value=product['price'] + " RUB")
            embed.add_embed_field(name='**Links**',
                                  value="[Cart](https://street-beat.ru/order/cart/)"
                                        "\n[Login](https://street-beat.ru/multicabinet/)")
            embed.set_timestamp()
            embed.set_footer(
                icon_url='https://sun9-16.userapi.com/impg/_6R59Fdndj2Pf-Iah-luprDvUMoLmpTJNJuwtQ/JD07kUgPelg.jpg?size=640x800&quality=96&proxy=1&sign=1f9b9db79ebf30a3a4e3aff1054925ff&type=album',
                text='THETR1XIK')
            webhook.add_embed(embed)
            webhook.execute()
            if product['sizes2'] != '':
                embed = DiscordEmbed(title=product['name'] + " on streetbeat.ru", url=product['link'], color=2544107,
                                     timestamp='now')
                embed.set_thumbnail(url=product['img'])
                embed.add_embed_field(name='**Sizes**', value=product['sizes2'])#,inline=(product['sizes1'] != '')
                embed.add_embed_field(name='**Price**', value=product['price'] + " RUB")
                embed.add_embed_field(name='**Links**',
                                      value="[Cart](https://street-beat.ru/order/cart/)"
                                            "\n[Login](https://street-beat.ru/multicabinet/)")
                embed.set_timestamp()
                embed.set_footer(
                    icon_url='https://sun9-16.userapi.com/impg/_6R59Fdndj2Pf-Iah-luprDvUMoLmpTJNJuwtQ/JD07kUgPelg.jpg?size=640x800&quality=96&proxy=1&sign=1f9b9db79ebf30a3a4e3aff1054925ff&type=album',
                    text='THETR1XIK')
                webhook.add_embed(embed)
                webhook.execute()
            else:
                pass
        else:
            if product['sizes2'] != '':
                embed = DiscordEmbed(title=product['name'] + " on streetbeat.ru", url=product['link'], color=2544107,
                                     timestamp='now')
                embed.set_thumbnail(url=product['img'])
                embed.add_embed_field(name='**Sizes**', value=product['sizes2'])  # ,inline=(product['sizes1'] != '')
                embed.add_embed_field(name='**Price**', value=product['price'] + " RUB")
                embed.add_embed_field(name='**Links**',
                                      value="[Cart](https://street-beat.ru/order/cart/)"
                                            "\n[Login](https://street-beat.ru/multicabinet/)")
                embed.set_timestamp()
                embed.set_footer(
                    icon_url='https://sun9-16.userapi.com/impg/_6R59Fdndj2Pf-Iah-luprDvUMoLmpTJNJuwtQ/JD07kUgPelg.jpg?size=640x800&quality=96&proxy=1&sign=1f9b9db79ebf30a3a4e3aff1054925ff&type=album',
                    text='THETR1XIK')
                webhook.add_embed(embed)
                webhook.execute()
        print(product['name'])
        print("CATCH IT IN DISCORD!")
