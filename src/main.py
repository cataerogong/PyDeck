import os.path
import os

from bottle import run, static_file, SimpleTemplate, get, redirect
import chardet
import yaml

_version = '0.1.0'
config = None
stpl = None

def open_any_enc(filename, mode='r', default_encoding='ascii'):
    """ open “自动识别文件编码”版本

    :param default_encoding: (str) 万一没有识别出文件编码时使用的缺省编码
    """
    r = None
    with open(filename, 'rb') as f:
        d = chardet.UniversalDetector()
        for l in f:
            d.feed(l)
            if d.done:
                break
        r = d.close()
    encoding = r['encoding'] if r and r['encoding'] else default_encoding
    return open(filename, mode, encoding=encoding)

def init():
    global config, stpl
    with open_any_enc('PyDeck.yaml', 'r') as f:
        config = yaml.safe_load(f)
    with open_any_enc('PyDeck.stpl', 'r') as f:
        stpl = SimpleTemplate(source=f)
    print('---- config:')
    print(yaml.dump(config, default_flow_style=False, sort_keys=False))

@get('/')
def mainpage():
    return stpl.render(
        version=_version,
        title=config['Title'],
        icon_width=int(100/config['Icons Per Line'])-2,
        show_label=config['Show Label'],
        apps=config.get('Apps', [])
        )
    # return template('PyDeck.stpl', title=config['Title'], apps=config['Apps'])

@get('/icon/<filename>')
def icon(filename: str):
    return static_file(filename, root=os.path.abspath('icon/'))

@get('/static/<filename>')
def icon(filename: str):
    return static_file(filename, root=os.path.abspath('static/'))

@get('/reload')
def reload():
    init()
    redirect('/')

@get('/action/<appid>')
def action(appid: str):
    for app in config['Apps']:
        if app['id'] == appid:
            print('---- Run app[{}] command={}'.format(appid, app['command']))
            # 只考虑运行在 Windows 平台，为了和服务器进程独立开，用了 START
            # 如果要在 linux 平台运行，需要修改这里
            os.system('START "[PyDeck] CMD" /I /D {} {}'.format(app.get('workdir', '.'), app['command']))
    redirect('/')

if __name__ == '__main__':
    print('---- version:', _version)
    init()
    run(host='0.0.0.0', port=config['Port'], server='paste')
