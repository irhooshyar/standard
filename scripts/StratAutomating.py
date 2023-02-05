from scripts.Persian import PersianAutomating

import after_response

@after_response.enable
def apply(folder_name, Country, tasks_list,host_url):
    try:
        
        PersianAutomating.persian_apply(folder_name, Country, tasks_list, host_url)

        Country.status = "Done"
        Country.save()

    except Exception as e:
        print("Error:" + str(e))
        Country.status = "Error: " + str(e)
        Country.save()
