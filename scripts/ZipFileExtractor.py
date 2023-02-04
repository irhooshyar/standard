import os
from pathlib import Path
from scripts import StratAutomating
from scripts.Persian import FolderCreator
from abdal import config
from scripts import Custom_ZipExtractor

def extractor(zip_file, newDoc, tasks_list,host_url):
    try:
        print('extracting')
        my_file = zip_file.file.path
        folder_name = str(os.path.basename(my_file))
        dot_index = folder_name.rfind('.')
        folder_name = folder_name[:dot_index]

        folder_path = str(Path(config.DATA_PATH, folder_name))

        FolderCreator.apply(folder_path)
        zip_ref = Custom_ZipExtractor.Custom_ZipExtractor(path=my_file, extract_path=folder_path)
        zip_ref.extract_all()

        StratAutomating.apply(folder_name, newDoc, tasks_list,host_url)
    except Exception as e:
        newDoc.status = "Error"
        newDoc.save()
