import math
import threading
from collections import Callable

from abdal import config

class Progress():
    def __init__(self, text='Progress', pLen=0 ):
        self.progress_value = 0
        self.progress_text = text
        self.progress_len = pLen
        self.progress_percent = 0

    def reset(self, text='Progress', pLen=0):
        #print('\n')
        self.progress_value = 0
        self.progress_text = text
        self.progress_len = pLen
        self.progress_percent = 0

    def progress(self, addValue=1):
        self.progress_value += addValue
        newPercent = int((self.progress_value * 100) / self.progress_len)
        total = 100
        if newPercent != self.progress_percent:
            self.progress_percent = newPercent
            #print("\033[A                                                   \033[A")
            #print(f'{self.progress_text}: {newPercent}/{total}')

    def setLen(self, num):
        self.progress_len = num

    def addLen(self, num):
        self.progress_len += num

    def setText(self, text):
        self.progress_text = text


class Parallel:
    numbers_of_thread = config.Thread_Count
    batch_size = config.BATCH_SIZE
    parallel_list = []
    result_key = []
    Progress = Progress

    def __init__(self):
        self.result_list = {}
        self.setResultSet(self.result_key)
        self.argument = {}
        self.statusProgress = Progress()
        self.er = False
        self.registerParallelPhase((self.start, self.parallelPhase))

    def registerParallelPhase(self, item):
        try:
            if type(item) == tuple and hasattr(item[0], '__call__') and hasattr(item[1], '__call__'):
                self.parallel_list.append(item)
            else:
                raise Exception(f"Bad type for register parallel phase. it must be tuple of two Function")
        except:
            raise Exception(f"Bad type for register parallel phase. it must be tuple of two Function")

    def addResult(self, key, value, threadNumber):
        try:
            self.result_list[key].append(value)
        except:
            raise Exception(f"key ('{key}') not set in result_key.\n result_key: {str(self.result_key)}")

    def setResultSet(self, resultKey):
        for key in resultKey:
            self.result_list[key]=[]

    def start(self, folderName, Country, **arg):
        return [] # or {}

    def end(self, res, **arg):
        pass

    def parallelPhase(self, li, threadNumber):
        pass

    def bulk_create_array(self, model, array, batch_size = batch_size ):
        slice_count = math.ceil(array.__len__() / batch_size)
        for i in range(slice_count):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, array.__len__())
            sub_list = array[start_idx:end_idx]
            model.objects.bulk_create(sub_list)

    def parallelRun(self, func, lists, **arg):

        arg = tuple(arg.values())

        thread_obj = []
        thread_number = 0

        for li in lists:
            thread = threading.Thread(target=func, args=(li, thread_number)+arg)
            thread_obj.append(thread)
            thread_number += 1
            thread.start()

        for thread in thread_obj:
            thread.join()

    def clearModel(self, Country):
        pass

    def apply(self, folderName, Country):
        self.clearModel(Country)

        # 1.
        for (preFunction, parallelFunction) in self.parallel_list:
            # start pre function
            self.statusProgress.reset()

            li = preFunction(folderName, Country, **self.argument)

            self.statusProgress.setLen(len(li))

            # slice
            if type(li) == dict:
                slice_li = self.sliceDict(li, self.numbers_of_thread)
            elif type(li) == list:
                slice_li = self.sliceList(li, self.numbers_of_thread)
            else:
                raise Exception(f"Type of something that returned from preFunction not list or dict: type={type(li)}")

            # run parallel
            self.parallelRun(parallelFunction, slice_li, **self.argument)

        # 2. end
        self.end(self.result_list, **self.argument)


    def sliceList(self, li, n):
        result_list = []
        step = math.ceil(li.__len__() / n)
        for i in range(n):
            start_idx = i * step
            end_idx = min(start_idx + step, li.__len__())
            result_list.append(li[start_idx:end_idx])

        return result_list

    def sliceDict(self, li, n):
        results = []
        docs_dict_keys = list(li.keys())
        step = math.ceil(li.keys().__len__() / n)
        for i in range(n):
            start_idx = i * step
            end_idx = min(start_idx + step, docs_dict_keys.__len__())
            res = {}
            for j in range(start_idx, end_idx):
                key = docs_dict_keys[j]
                res[key] = li[key]
            results.append(res)

        return results

    def getResultList(self):
        return self.result_list

    def getResult(self, key):
        return self.result_list[key]


