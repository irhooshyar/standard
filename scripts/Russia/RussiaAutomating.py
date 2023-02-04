from scripts.Russia import CreateFolder, \
    DocsNgramExtractor, DocsParagraphsExtractor, DocFeaturesExtractor, \
 DocsTFIDFExtractor, DocsListExtractor, Preprocessing , DocsApprovalReferenceExtractor

import after_response


def russia_apply(folder_name, Country, tasks_list, host_url):
    print(folder_name)

    tasks_list = tasks_list.split("_")

    if "renameFilesToStandard" in tasks_list:
        print("1. renameFilesToStandard")
        Preprocessing.renameFilesToStandard(folder_name)
        Country.status = "renameFilesToStandard"
        Country.save()

    if "Preprocess" in tasks_list:
        print("2. CreateFolder")
        CreateFolder.apply(folder_name)
        print("3. DocsListExtractor")
        DocsListExtractor.apply(folder_name, Country)
        print("11. DocsParagraphsExtractor")
        DocsParagraphsExtractor.apply(folder_name, Country)
        Country.status = "Preprocess"
        Country.save()

    # if "StaticDataImportDB" in tasks_list:
    #     print("5. StaticDataImportDB")
    #     StaticDataImportDB.apply(folder_name, Country)
    #     Country.status = "StaticDataImportDB"
    #     Country.save()

    if "DocsTFIDFExtractor" in tasks_list:
        print("5. DocsTFIDFExtractor")
        DocsTFIDFExtractor.apply(folder_name, Country)
        Country.status = "DocsTFIDFExtractor"
        Country.save()

    if "Docs2gramExtractor" in tasks_list:
        print("6. Docs2gramExtractor")
        DocsNgramExtractor.apply(folder_name, 2, Country)
        Country.status = "Docs2gramExtractor"
        Country.save()

    if "Docs3gramExtractor" in tasks_list:
        print("7. Docs3gramExtractor")
        DocsNgramExtractor.apply(folder_name, 3, Country)
        Country.status = "Docs3gramExtractor"
        Country.save()

    if "DocFeaturesExtractor" in tasks_list:
        print("9. DocFeaturesExtractor")
        DocFeaturesExtractor.apply(folder_name, Country)
        Country.status = "DocFeaturesExtractor"
        Country.save()

    # if "DocsInvertedIndexExtractor" in tasks_list:
    #     print("10. DocsInvertedIndexExtractor")
    #     DocsInvertedIndexExtractor.apply(folder_name, Country)
    #     print("13. DocsTitleInvertedIndexExtractor")
    #     DocsTitleInvertedIndexExtractor.apply(folder_name, Country)
    #     Country.status = "DocsInvertedIndexExtractor"
    #     Country.save()

    if "DocsApprovalReferenceExtractor" in tasks_list:
        print("10. DocsApprovalReferenceExtractor")
        DocsApprovalReferenceExtractor.apply(folder_name, Country)
        Country.status = "DocsApprovalReferenceExtractor"
        Country.save()


    Country.status = "Done"
    Country.save()