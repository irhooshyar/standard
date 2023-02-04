import os

import pandas as pd

base_dir = "extracted_data"
files_list_dir = base_dir+"/data.xlsx"
skipped_pages_list_dir = base_dir+"/skipped_pages.xlsx"


if not os.path.isdir(base_dir):
    os.mkdir(base_dir)

if not os.path.isfile(files_list_dir):
    df = pd.DataFrame({'pid': [],'name':[],'date':[],'approval':[]})
    df.to_excel(files_list_dir, index=False)

if not os.path.isfile(skipped_pages_list_dir):
    df = pd.DataFrame({'pages': []})
    df.to_excel(skipped_pages_list_dir, index=False)

# if not os.path.isfile(ref_list_dir):
#     df = pd.DataFrame({'act1': [],'act2':[]})
#     df.to_excel(ref_list_dir, index=False)