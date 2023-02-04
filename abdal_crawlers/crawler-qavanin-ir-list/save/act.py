import pandas as pd
from openpyxl import load_workbook

from db.models import Law
from save import files_list_dir

excel = pd.read_excel(files_list_dir,)
wb = load_workbook(files_list_dir)
ws = wb.worksheets[0]



def already_added(id_:str):
    return Law.objects.filter(pid=int(id_)).count() > 0

