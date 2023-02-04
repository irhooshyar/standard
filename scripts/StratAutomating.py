from scripts.Persian import PersianAutomating
from scripts.English import EnglishAutomating
from scripts.Russia import RussiaAutomating

import after_response

@after_response.enable
def apply(folder_name, Country, tasks_list,host_url):
    try:
        if Country.language == "فارسی":
            PersianAutomating.persian_apply(folder_name, Country, tasks_list, host_url)

        elif Country.language == "انگلیسی":
            EnglishAutomating.english_apply(folder_name, Country, tasks_list, host_url)

        elif Country.language == "روسی":
            RussiaAutomating.russia_apply(folder_name, Country, tasks_list, host_url)
            
        elif Country.language == "کتاب":
            PersianAutomating.persian_apply(folder_name, Country, tasks_list, host_url)

        elif Country.language == "استاندارد":
            PersianAutomating.persian_apply(folder_name, Country, tasks_list, host_url)

        Country.status = "Done"
        Country.save()

    except Exception as e:
        print("Error:" + str(e))
        Country.status = "Error: " + str(e)
        Country.save()
