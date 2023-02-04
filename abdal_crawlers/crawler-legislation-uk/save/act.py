import os.path
import requests
from openpyxl import load_workbook

from db.models import Act
from save import files_dir, txt_files_dir, files_list_dir
from utils import fix_dir_name


def dl_file(url, name, _dir):
    path = files_dir + "/" + _dir + "/" + name
    if os.path.isfile(files_dir + "/" + name):
        print(f'file {url} already exist as {path} .skipping...')
        return
    try:
        r = requests.get(url)
        open(path, 'wb').write(r.content)
    except:
        return None
    return True


def save_txt(name, text):
    try:
        f = open(txt_files_dir + "/" + fix_dir_name(name).strip() + ".txt", "w", encoding="utf-8")
        for line in text:
            f.write(line)
        f.close()
    except Exception as e:
        print(f'failed to save file {name}.')
        return False
    return True


def load_missing_text():
    acts = Act.objects.all().exclude(text="empty").exclude(text="blocked")
    total = acts.count()
    count = 0
    for act in acts:
        save_txt(act.title, act.text)
        if count % 100 == 0:
            print(f'{count / total}% of {total} done.')
        count += 1


def export_excel():
    wb2 = load_workbook(files_list_dir)
    ws2 = wb2.worksheets[0]
    count = 0
    acts = Act.objects.all().exclude(text="empty").exclude(text="blocked")
    total = acts.count()
    for act in acts:
        if act.text != "":
            save_txt(act.title, act.text)
        ws2.append(
            [act.title, act.type, act.year, act.number, '+' if act.text != "" else '-'])
        if count % 100 == 0:
            print(f'{count / total}% of {total} done.')
        count += 1
    wb2.save(files_list_dir)
