# from os import listdir
# from os.path import isfile, join
#
# from save import xht_files_dir, txt_files_dir_converted
# from utils import convert_xht_to_txt,convert_xht_to_txt_2

# only_files = [f for f in listdir(xht_files_dir) if isfile(join(xht_files_dir, f))]

# for index,file_ in enumerate(only_files):
#     print(f'doc {index+1}.{file_} converted.')
#     f = open(xht_files_dir+"/"+file_, "r")
#     text = f.read()
#     text = convert_xht_to_txt_2(text)
#     f = open(txt_files_dir_converted+"/"+file_[:-3]+"txt", "w")
#     for line in text:
#         f.write(line)
#     f.close()
    # break


# f = open(xht_files_dir+"/"+"The Air Navigation (Restriction of Flying) (Abingdon Air and Country Show) Regulations 2021.xht", "r")
# text = f.read()
# text = convert_xht_to_txt_2(text)
# if len(text) == 0:
#     print("hello")
# f = open(txt_files_dir_converted+"/"+"The Air Navigation (Restriction of Flying) (Abingdon Air and Country Show) Regulations 2021."+"txt", "w")
# for line in text:
#     f.write(line)
# f.close()
# import re
#
# regexes = [
#     r'“.*”',
#
# ]
#
# pair = re.compile(regexes[0])
# print(pair.search('““dalam means”dwdw'))