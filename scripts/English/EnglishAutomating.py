from scripts.English import CreateFolder, DocsInvertedIndexExtractor, \
    DocsNgramExtractor, DocsParagraphsExtractor, DocFeaturesExtractor, \
    DocsTitleInvertedIndexExtractor, DocsTFIDFExtractor, DocsListExtractor, \
    Preprocessing, DocsReferencesExtractor, StaticDataImportDB, DocsDefinitionsExtractor, \
    DocsApprovalReferenceExtractor, DocsSubjectExtractor, AINamedEntitiesExtractor, \
    DocsCreateDocumentsListCubeData, DocsCompleteJsonField, DocsActorsExtractor

import after_response
import time

def english_apply(folder_name, Country, tasks_list, host_url):
    tasks_list = tasks_list.split("_")
    print("*************************************************")
    
    print("0. ConvertPdfsToTxt")
    Country.status = "ConvertPdfsToTxt"
    Country.save()
    Preprocessing.convert_all_pdfs_to_txt(folder_name)
    
    if "renameFilesToStandard" in tasks_list:
        Country.status = "renameFilesToStandard"
        Country.save()

        print("1. renameFilesToStandard")
        Preprocessing.renameFilesToStandard(folder_name)

    if "Preprocess" in tasks_list: ###
        Country.status = "Preprocess"
        Country.save()

        print("3. DocsListExtractor")
        DocsListExtractor.apply(folder_name, Country)

        print("11. DocsParagraphsExtractor")
        DocsParagraphsExtractor.apply(folder_name, Country)

    if "StaticDataImportDB" in tasks_list:
        Country.status = "StaticDataImportDB"
        Country.save()

        print("5. StaticDataImportDB")
        StaticDataImportDB.apply(folder_name, Country)

    if "DocsTFIDFExtractor" in tasks_list:
        Country.status = "DocsTFIDFExtractor"
        Country.save()

        print("5. DocsTFIDFExtractor")
        DocsTFIDFExtractor.apply(folder_name, Country)

    if "DocFeaturesExtractor" in tasks_list:
        Country.status = "DocFeaturesExtractor"
        Country.save()

        print("9. DocFeaturesExtractor")
        DocFeaturesExtractor.apply(folder_name, Country)

    if "DocsInvertedIndexExtractor" in tasks_list:
        Country.status = "DocsInvertedIndexExtractor"
        Country.save()

        print("10. DocsInvertedIndexExtractor")
        DocsInvertedIndexExtractor.apply(folder_name, Country)

        Country.status = "DocsTitleInvertedIndexExtractor"
        Country.save()

        print("13. DocsTitleInvertedIndexExtractor")
        DocsTitleInvertedIndexExtractor.apply(folder_name, Country)

    if "DocsReferencesExtractor" in tasks_list:
        Country.status = "DocsReferencesExtractor"
        Country.save()

        print("15. DocsReferencesExtractor")
        f = DocsReferencesExtractor.DocsReferencesExtractor()
        f.apply(folder_name, Country)
        del f

    if "Docs2gramExtractor" in tasks_list:
        Country.status = "Docs2gramExtractor"
        Country.save()

        print("6. Docs2gramExtractor")
        DocsNgramExtractor.apply(folder_name, 2, Country)

    if "Docs3gramExtractor" in tasks_list:
        Country.status = "Docs3gramExtractor"
        Country.save()

        print("7. Docs3gramExtractor")
        DocsNgramExtractor.apply(folder_name, 3, Country)

    if "DocsDefinitionsExtractor" in tasks_list:
        Country.status = "DocsDefinitionsExtractor"
        Country.save()

        print("9. DocsDefinitionsExtractor")
        DocsDefinitionsExtractor.apply(folder_name, Country)

    if "DocsApprovalReferenceExtractor" in tasks_list:
        Country.status = "DocsApprovalReferenceExtractor"
        Country.save()

        print("9. DocsApprovalReferenceExtractor")
        DocsApprovalReferenceExtractor.apply(folder_name, Country)

    if "DocsActorsExtractor" in tasks_list:
        Country.status = "DocsActorsExtractor"
        Country.save()

        print("9. DocsActorsExtractor")
        DocsActorsExtractor.apply(folder_name, Country)

    if "DocsSubjectExtractor" in tasks_list:
        Country.status = "DocsSubjectExtractor"
        Country.save()

        # print("15. DocsSubjectExtractor")
        # f = DocsSubjectExtractor.DocsSubjectExtractor()
        # f.apply(folder_name, Country)
        #del f

    if "DocsCreateDocumentsListCubeData" in tasks_list:
        Country.status = "DocsCompleteJsonField"
        Country.save()

        print("10. DocsCompleteJsonField")
        DocsCompleteJsonField.apply(folder_name, Country)

        Country.status = "DocsCreateJsonList"
        Country.save()

        print("11. DocsCreateDocumentsListCubeData")
        DocsCreateDocumentsListCubeData.apply(folder_name, Country)

    if "AINamedEntitiesExtractor" in tasks_list:
        Country.status = "AINamedEntitiesExtractor"
        Country.save()

        print("9. AINamedEntitiesExtractor")
        AINamedEntitiesExtractor.apply(folder_name, Country)

    Country.status = "Done"
    Country.save()