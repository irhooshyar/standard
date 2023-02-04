import shutil

from save import base_dir

shutil.make_archive("./files", 'zip', f"{base_dir}/files/txt")
# shutil.make_archive(f"{base_dir}/converted", 'zip', "./qavanin-ir-converted-2000")
