import shutil

from crawler_data import base_dir

shutil.make_archive("./qavanin", 'zip', f"{base_dir}/files/")
# shutil.make_archive(f"{base_dir}/converted", 'zip', "./qavanin-ir-converted-2000")
