from openpyxl import load_workbook

from db.models import Law
from save import files_list_dir


def trim(string:str):
    return string.strip()

def to_excel():
    wb2 = load_workbook(files_list_dir)
    ws2 = wb2.worksheets[0]
    count = 1
    for law in Law.objects.all():
        print(f'exporting {count}. {law}')
        ws2.append(
            [law.pid, law.name, law.data, law.approve])
        count += 1
    wb2.save(files_list_dir)

