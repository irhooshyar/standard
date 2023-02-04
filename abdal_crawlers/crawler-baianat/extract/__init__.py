base_url = "https://farsi.khamenei.ir/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                  'Safari/537.36 QIHU 360SE '
}

types = {
    'speech?nt=2&year=':{'name':'baianat','url':'speech-content?id='},
    'speech?nt=32&year=':{'name':'eblaghie','url':'news-content?id='}
}
types_={type__['name']:type__['url'] for type__ in types.values()}