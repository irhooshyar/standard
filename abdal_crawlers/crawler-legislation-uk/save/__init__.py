import os

import pandas as pd

base_dir = "extracted_data"
files_list_dir = base_dir + "/files.xlsx"
files_dir = base_dir + "/files"
txt_files_dir = files_dir + "/txt"
pdf_files_dir = files_dir + "/pdf"

if not os.path.isdir(base_dir):
    os.mkdir(base_dir)

if not os.path.isdir(files_dir):
    os.mkdir(files_dir)

if not os.path.isdir(txt_files_dir):
    os.mkdir(txt_files_dir)

if not os.path.isdir(pdf_files_dir):
    os.mkdir(pdf_files_dir)

if not os.path.isfile(files_list_dir):
    df = pd.DataFrame({'title': [], 'type': [], 'year': [], 'number': [], 'txt': []})
    df.to_excel(files_list_dir, index=False)
