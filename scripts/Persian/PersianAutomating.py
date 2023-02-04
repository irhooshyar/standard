
from scripts.Persian import DocsCreateSubjectStatisticsCubeData, DocsCreateTemplatePanelsCubeData, \
    DocsSubjectExtractor, DocsKeywordsExtractor, DocsInvertedIndexExtractor, \
    DocsNgramExtractor, DocsLevelExtractor, DocsParagraphsExtractor, DocFeaturesExtractor, \
    DocsTitleInvertedIndexExtractor, DocsDefinitionsExtractor, DocsTFIDFExtractor, DocsListExtractor, \
    DocsReferencesExtractor, Preprocessing, DocsTypeExtractor, StandardsListExtractor, StaticDataImportDB, \
    DocsGeneralDefinitionsExtractor, DocsActorsExtractor3, DocsActorsExtractor4, \
    DocsRegulatorsExtractor2, DocsRegulatorsExtractor3, DocsCreateDocumentsListCubeData, \
    DocsClauseExtractor, DocsCreateSubjectCubeData, \
    DocsCreateVotesCubeData, DocsCompleteJsonField, \
    DocsCollectiveActorsExtractor, DocsExecutiveParagraphsExtractor, DocsExecutiveClausesExtractor, \
    DocsAnalysisLeadershipSlogan, DocsOperatorsExtractor, DocsCreateRegularityLifeCycleCubeData, \
    DocsGeneralActorsExtractor, DocCreateBusinessAdvisorCubeData, DocsCreateMandatoryRegulationsCubeData, \
    DocsCreatePrinciplesCubeData, AITopicLDA, DocsActorsTimeSeriesDataExtractor, CompareDataSet, \
    DocsGraphCubeData, DocsJudgmentGraphNodesCube, DocsJudgmentGraphEdgesCube, \
    DocsStandardGraphNodesCube, DocsStandardGraphEdgesCube, \
    DocsCreateActorInformationStackChartCubeData, \
    ActorsARIMAPrediction, Test, DocsJudgementReferencesGraphCubeData, FindOrganizationNameDocuments, \
    DocsReferencesExtractor2, DocsSubjectAreaExtractor, DocsCreateAreaGraph, AIParagraphTopicLDA

from scripts.Persian import DocsRevokedExtractor, DocsSubjectAreaCubeData, DocsCancelledExtractor, ClusteringGraphData

from scripts.Persian.DocsDefinitionsExtractor import DocsDefinitionsExtractor
from scripts.Persian import DocsParagraphsClustering , SubjectParagraphExtractor, DocAnalysisKnowledgeGraph, DocAnalysisKnowledgeGraphPOS
# from scripts.Persian.DocsInvertedIndexExtractor import DocsInvertedIndexExtractor
from scripts.Persian import DocsSubjectExtractor2,DocsSubjectExtractor3
from scripts.Persian import DocsParagraphsClusteringCubeData,LDAGraphData \
    , ActorTimeSeriesPrediction,AdvanceARIMAExtractor
from datetime import datetime

from abdal.settings import LOCAL_SETTING
ENABLE_BERT = LOCAL_SETTING['ENABLE_BERT']

if ENABLE_BERT:
    from scripts.Persian import AIDocSimilarity

# ------------------- ES Configs -----------------------------------
from abdal.es_config import INGEST_ENABLED
from es_scripts import IngestDocumentsToElastic,IngestParagraphsToElastic
# ------------------- ES Configs -----------------------------------


def persian_apply(folder_name, Country, tasks_list, host_url):
    print("start at: ", datetime.now().strftime("%H:%M:%S"))

    tasks_list = tasks_list.split("_")


    print("0. ConvertPdfsToTxt")
    Country.status = "ConvertPdfsToTxt"
    Country.save()
    Preprocessing.convert_all_pdfs_to_txt(folder_name)

    if "renameFilesToStandard" in tasks_list: ####
        print("1. renameFilesToStandard")
        Country.status = "renameFilesToStandard"
        Country.save()
        Preprocessing.renameFilesToStandard(folder_name)

    if "Preprocess" in tasks_list: ####

        Country.status = "DocsListExtractor"
        Country.save()

        # if Country.language == "استاندارد":
        #     print("2. StandardsListExtractor")
        #     StandardsListExtractor.apply(folder_name, Country)
        # else:
        print("2. DocsListExtractor")
        DocsListExtractor.apply(folder_name, Country)
        # -------------------------------------------------------

        Country.status = "DocsParagraphsExtractor"
        Country.save()

        print("3. DocsParagraphsExtractor")
        DocsParagraphsExtractor.apply(folder_name, Country)

    # Test.apply(folder_name, Country)

    if "StaticDataImportDB" in tasks_list: ####
        Country.status = "StaticDataImportDB"
        Country.save()

        print("4. StaticDataImportDB")
        StaticDataImportDB.apply(folder_name, Country)

    if "DocsTFIDFExtractor" in tasks_list: ####
        Country.status = "DocsTFIDFExtractor"
        Country.save()

        print("5. DocsTFIDFExtractor")
        DocsTFIDFExtractor.apply(folder_name, Country)

    if "Docs2gramExtractor" in tasks_list: ####
        Country.status = "Docs2gramExtractor"
        Country.save()

        print("6. Docs2gramExtractor")
        DocsNgramExtractor.apply(folder_name, 2, Country)

    if "Docs3gramExtractor" in tasks_list: ####
        Country.status = "Docs3gramExtractor"
        Country.save()

        print("7. Docs3gramExtractor")
        DocsNgramExtractor.apply(folder_name, 3, Country)

    if "DocFeaturesExtractor" in tasks_list: ####
        Country.status = "DocFeaturesExtractor"
        Country.save()

        print("8. DocFeaturesExtractor")
        DocFeaturesExtractor.apply(folder_name, Country)

    if "DocsSubjectExtractor" in tasks_list: ####
        Country.status = "DocsSubjectExtractor"
        Country.save()

        print("9. DocsSubjectExtractor")
        DocsSubjectExtractor.apply(folder_name, Country)

    if "DocsSubjectAreaExtractor" in tasks_list: ####
        Country.status = "DocsSubjectAreaExtractor"
        Country.save()

        print("9. DocsSubjectAreaExtractor")
        DocsSubjectAreaExtractor.apply(folder_name, Country)

    if "DocsTypeExtractor" in tasks_list: ####
        Country.status = "DocsTypeExtractor"
        Country.save()

        print("11. DocsTypeExtractor")
        DocsTypeExtractor.apply(folder_name, Country)

    if "DocsLevelExtractor" in tasks_list: ####
        Country.status = "DocsLevelExtractor"
        Country.save()

        print("10. DocsLevelExtractor")
        DocsLevelExtractor.apply(folder_name, Country)

    if "DocsGeneralDefinitionsExtractor" in tasks_list: ####
        Country.status = "DocsGeneralDefinitionsExtractor"
        Country.save()

        print("12. DocsGeneralDefinitionsExtractor")
        DocsGeneralDefinitionsExtractor.apply(folder_name, Country)

    if "DocsInvertedIndexExtractor" in tasks_list: ####
        Country.status = "DocsInvertedIndexExtractor"
        Country.save()

        print("13. DocsInvertedIndexExtractor")
        DocsInvertedIndexExtractor.apply(folder_name, Country)

        Country.status = "DocsTitleInvertedIndexExtractor"
        Country.save()

        print("14. DocsTitleInvertedIndexExtractor")
        DocsTitleInvertedIndexExtractor.apply(folder_name, Country)

    if "DocsKeywordsExtractor" in tasks_list: ####
        Country.status = "DocKeywordsExtractor"
        Country.save()

        print("15. DocsKeywordsExtractor")
        DocsKeywordsExtractor.apply(folder_name, Country)


    # ----------------- Ingestions ---------------------------
    if INGEST_ENABLED:

        # --- Ingest Documents
        if "IngestDocumentsToElastic" in tasks_list:
            Country.status = "IngestDocumentsToElastic"
            Country.save()

            print("40. IngestDocumentsToElastic.")
            IngestDocumentsToElastic.apply(folder_name, Country)


        # --- Ingest Paragraphs
        if "IngestParagraphsToElastic" in tasks_list:
            Country.status = "IngestParagraphsToElastic"
            Country.save()

            print("41. IngestParagraphsToElastic.")
            IngestParagraphsToElastic.apply(folder_name, Country,1)



    # New
    if "DocsSubjectExtractor2" in tasks_list: ####
        Country.status = "DocsSubjectExtractor2"
        Country.save()

        print("15. DocsSubjectExtractor2")
        DocsSubjectExtractor2.apply(folder_name, Country)


    # --------------------------------------------------------

    if "DocsReferencesExtractor" in tasks_list: #### No RUN
        Country.status = "DocsReferencesExtractor"
        Country.save()

        print("16. DocsReferencesExtractor")
        # f = DocsReferencesExtractor.DocsReferencesExtractor()
        # f.apply(folder_name, Country)
        # del f

        DocsReferencesExtractor2.apply(folder_name, Country)

    if "DocsDefinitionsExtractor" in tasks_list: ####
        Country.status = "DocsDefinitionsExtractor"
        Country.save()

        print("17. DocsDefinitionsExtractor")
        f = DocsDefinitionsExtractor()
        f.apply(folder_name, Country)
        del f
        # DocsDefinitionsExtractor.apply(folder_name, Country)

    if "DocsActorsExtractor" in tasks_list: ####
        Country.status = "DocsActorsExtractor"
        Country.save()

        print("12. DocsActorsExtractor")
        DocsActorsExtractor4.apply(folder_name, Country)


    if "DocsGeneralActorsExtractor" in tasks_list: ####
        Country.status = "DocsGeneralActorsExtractor"
        Country.save()

        print("19. DocsGeneralActorsExtractor")
        DocsGeneralActorsExtractor.apply(folder_name, Country)

    if "DocsCollectiveActorsExtractor" in tasks_list: ####
        Country.status = "DocsCollectiveActorsExtractor"
        Country.save()

        print("20. DocsCollectiveActorsExtractor")
        DocsCollectiveActorsExtractor.apply(folder_name, Country)

    if "DocsRegulatorsExtractor" in tasks_list: ####
        Country.status = "DocsRegulatorsExtractor"
        Country.save()

        print("21. DocsRegulatorsExtractor")
        DocsRegulatorsExtractor3.apply(folder_name, Country)

    if "DocsOperatorsExtractor" in tasks_list: ####
        Country.status = "DocsOperatorsExtractor"
        Country.save()

        print("22. DocsOperatorsExtractor")
        DocsOperatorsExtractor.apply(folder_name, Country)


    if "DocsActorsTimeSeriesDataExtractor" in tasks_list: ####
        Country.status = "DocsActorsTimeSeriesDataExtractor"
        Country.save()

        print("22. DocsActorsTimeSeriesDataExtractor")
        DocsActorsTimeSeriesDataExtractor.apply(folder_name, Country)

    if "ActorTimeSeriesPrediction" in tasks_list: ####
        Country.status = "ActorTimeSeriesPrediction"
        Country.save()

        print("22. ActorTimeSeriesPrediction")
        ActorTimeSeriesPrediction.apply(folder_name, Country)

    if "AdvanceARIMAExtractor" in tasks_list: ####
        Country.status = "AdvanceARIMAExtractor"
        Country.save()

        print("22. AdvanceARIMAExtractor")
        AdvanceARIMAExtractor.apply(folder_name, Country)


    if "DocsParagraphsClustering" in tasks_list: ####
        Country.status = "DocsParagraphsClustering"
        Country.save()

        print("12. DocsParagraphsClustering")
        DocsParagraphsClustering.apply(folder_name, Country)

    if "DocsParagraphsClusteringCubeData" in tasks_list: ####
        Country.status = "DocsParagraphsClusteringCubeData"
        Country.save()

        print("13. DocsParagraphsClusteringCubeData")
        DocsParagraphsClusteringCubeData.apply(folder_name, Country)
    # ----------------- CUBE DATA ---------------------------

    if "DocsCreateDocumentsListCubeData" in tasks_list: ####
        Country.status = "DocsCompleteJsonField"
        Country.save()

        print("23. DocsCompleteJsonField")
        DocsCompleteJsonField.apply(folder_name, Country)

        Country.status = "DocsCreateJsonList"
        Country.save()

        print("24. DocsCreateJsonList")
        DocsCreateDocumentsListCubeData.apply(folder_name, Country)

    if "DocsCreateSubjectCubeData" in tasks_list: ####
        Country.status = "DocsCreateSubjectCubeData"
        Country.save()

        print("25. DocsCreateSubjectCubeData.")
        DocsCreateSubjectCubeData.apply(folder_name, Country, host_url)

    if "DocsCreateVotesCubeData" in tasks_list:  ####
        Country.status = "DocsCreateVotesCubeData"
        Country.save()

        print("26. DocsCreateVotesCubeData.")
        DocsCreateVotesCubeData.apply(folder_name, Country, host_url)

    if "DocsCreateSubjectStatisticsCubeData" in tasks_list: ####
        Country.status = "DocsCreateSubjectStatisticsCubeData"
        Country.save()

        print("27. DocsCreateSubjectStatisticsCubeData")
        DocsCreateSubjectStatisticsCubeData.apply(folder_name, Country)

    if "DocsCreateTemplatePanelsCubeData" in tasks_list:
        Country.status = "DocsCreateTemplatePanelsCubeData"
        Country.save()

        print("28. DocsCreateTemplatePanelsCubeData.")
        DocsCreateTemplatePanelsCubeData.apply(folder_name, Country, host_url, "All")

    if "DocsAnalysisLeadershipSlogan" in tasks_list:
        Country.status = "DocsAnalysisLeadershipSlogan"
        Country.save()

        print("30. DocsAnalysisLeadershipSlogan")
        DocsAnalysisLeadershipSlogan.apply(folder_name, Country)

    if "DocsCreatePrinciplesCubeData" in tasks_list:
        Country.status = "DocsCreatePrinciplesCubeData"
        Country.save()

        print("31. DocsCreatePrinciplesCubeData.")
        DocsCreatePrinciplesCubeData.apply(folder_name, Country, host_url)

    if "DocCreateBusinessAdvisorCubeData" in tasks_list:
        Country.status = "DocCreateBusinessAdvisorCubeData"
        Country.save()

        print("32. DocCreateBusinessAdvisorCubeData.")
        DocCreateBusinessAdvisorCubeData.apply(folder_name, Country, host_url)

    if "DocsCreateRegularityLifeCycleCubeData" in tasks_list:
        Country.status = "DocsCreateRegularityLifeCycleCubeData"
        Country.save()

        print("33. DocsCreateRegularityLifeCycleCubeData.")
        DocsCreateRegularityLifeCycleCubeData.apply(folder_name, Country, host_url)

    # if "DocsExecutiveParagraphsExtractor" in tasks_list:
    #     Country.status = "DocsExecutiveParagraphsExtractor"
    #     Country.save()
    #
    #     print("34. DocsExecutiveParagraphsExtractor.")
    #     DocsExecutiveParagraphsExtractor.apply(folder_name, Country)

    if "DocsJudgmentGraphCube" in tasks_list:
        Country.status = "DocsJudgmentGraphCube"
        Country.save()

        print("35. DocsJudgmentGraphNodesCube.")
        DocsJudgmentGraphNodesCube.apply(folder_name, Country)

        print("35. DocsJudgmentGraphEdgesCube.")
        DocsJudgmentGraphEdgesCube.apply(folder_name, Country)

    if "DocsJudgementReferencesGraphCube" in tasks_list:
        Country.status = "DocsJudgementReferencesGraphCube"
        Country.save()

        print("35. DocsJudgementReferencesGraphCube.")
        DocsJudgementReferencesGraphCubeData.apply(folder_name, Country)


    if "DocsStandardGraphCube" in tasks_list:
        Country.status = "DocsStandardGraphCube"
        Country.save()

        print("35. DocsStandardGraphNodesCube.")
        DocsStandardGraphNodesCube.apply(folder_name, Country)

        print("35. DocsStandardGraphEdgesCube.")
        DocsStandardGraphEdgesCube.apply(folder_name, Country)

    # if "DocsClauseExtractor" in tasks_list:
    #     Country.status = "DocsClauseExtractor"
    #     Country.save()
    #
    #     print("35. DocsClauseExtractor.")
    #     DocsClauseExtractor.apply(folder_name, Country)

    if "DocsGraphCubeData" in tasks_list:
        Country.status = "DocsGraphCubeData"
        Country.save()

        print("35. DocsGraphCubeData")
        DocsGraphCubeData.apply(folder_name, Country, host_url)

    if "DocsAreaGraphCubeData" in tasks_list:
        Country.status = "DocsAreaGraphCubeData"
        Country.save()

        print("35. DocsAreaGraphCubeData")
        DocsCreateAreaGraph.apply(folder_name, Country)

    if "DocsCreateMandatoryRegulationsCubeData" in tasks_list:
        Country.status = "DocsCreateMandatoryRegulationsCubeData"
        Country.save()

        print("36. DocsCreateMandatoryRegulationsCubeData.")
        DocsCreateMandatoryRegulationsCubeData.apply(folder_name, Country, host_url)

    # if "DocsExecutiveClausesExtractor" in tasks_list:
    #     Country.status = "DocsExecutiveClausesExtractor"
    #     Country.save()
    #
    #     print("37. DocsExecutiveClausesExtractor.")
    #     DocsExecutiveClausesExtractor.apply(folder_name, Country)

    if "CompareDataSet" in tasks_list:
        Country.status = "CompareDataSet"
        Country.save()

        print("38. CompareDataSet.")
        CompareDataSet.apply(folder_name)
    
    if "DocsCreateActorInformationStackChartCubeData" in tasks_list:
        Country.status = "DocsCreateActorInformationStackChartCubeData"
        Country.save()

        print("39. DocsCreateActorInformationStackChartCubeData.")
        DocsCreateActorInformationStackChartCubeData.apply(folder_name, Country, host_url)


    if "FindOrganizationNameDocuments" in tasks_list:
        Country.status = "FindOrganizationNameDocuments"
        Country.save()

        print("41. FindOrganizationNameDocuments.")
        FindOrganizationNameDocuments.apply(folder_name, Country)

    if "DocsRevokedExtractor" in tasks_list:
        Country.status = "DocsRevokedExtractor"
        Country.save()

        print("40. DocsRevokedExtractor.")
        DocsRevokedExtractor.apply(folder_name, Country)

        print("40. DocsCancelledExtractor.")
        DocsCancelledExtractor.apply(folder_name, Country)

    if "DocsSubjectAreaCubeData" in tasks_list:
        Country.status = "DocsSubjectAreaCubeData"
        Country.save()

        print("40. DocsSubjectAreaCubeData.")
        DocsSubjectAreaCubeData.apply(folder_name, Country,host_url)


    # ----------------- AI ---------------------------
    if "AIDocSimilarity" in tasks_list:
        Country.status = "AIDocSimilarity"
        Country.save()

        print("38. AIDocSimilarity.")
        if ENABLE_BERT:
            AIDocSimilarity.apply(folder_name, Country)
        else:
            print("Bert is disable!")

    if "AITopicLDA" in tasks_list:
        Country.status = "AITopicLDA"
        Country.save()

        print("39. AITopicLDA.")
        AITopicLDA.apply(folder_name, Country)

    if "AIParagraphTopicLDA" in tasks_list:
        Country.status = "AIParagraphTopicLDA"
        Country.save()

        print("44. AIParagraphTopicLDA.")
        AIParagraphTopicLDA.apply(folder_name, Country)

    if "SubjectParagraphExtractor" in tasks_list:
        Country.status = "SubjectParagraphExtractor"
        Country.save()

        print("43. SubjectParagraphExtractor.")
        SubjectParagraphExtractor.apply(folder_name, Country)

    if "ClusteringGraphData" in tasks_list:
        Country.status = "ClusteringGraphData"
        Country.save()

        print("43. ClusteringGraphData.")
        ClusteringGraphData.apply(Country)

    if "LDAGraphData" in tasks_list:
        Country.status = "LDAGraphData"
        Country.save()

        print("43. LDAGraphData.")
        LDAGraphData.apply(Country)

    if "DocAnalysisKnowledgeGraph" in tasks_list:
        Country.status = "DocAnalysisKnowledgeGraph"
        Country.save()

        print("44. DocAnalysisKnowledgeGraph.")
        DocAnalysisKnowledgeGraph.apply(folder_name, Country)

    if "DocAnalysisKnowledgeGraphPOS" in tasks_list:
        Country.status = "DocAnalysisKnowledgeGraphPOS"
        Country.save()

        print("45. DocAnalysisKnowledgeGraphPOS.")
        DocAnalysisKnowledgeGraphPOS.apply(folder_name, Country)

    print("finished at: ", datetime.now().strftime("%H:%M:%S"))

