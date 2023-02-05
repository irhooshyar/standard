from django.contrib import admin
from django.urls import path, include
from doc import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_zip_file, name='zip'),
    path('update/<int:id>/<str:language>/', views.update_doc, name='update'),
    path('delete/<int:id>/<str:language>/', views.delete_doc, name='delete'),

    path('get_task_list/', views.get_task_list, name='get_task_list'),

    path('slogan_key_synonymous_words/<str:language>/', views.slogan_key_synonymous_words,
         name='slogan_key_synonymous_words'),
    # ---------------- temporary url , will be removed after level detection bug is fixed ----------------#
    path('detect_level/<int:id>/', views.detect_level, name='detect_level'),
    path('static_data_import_db/<int:id>/<str:language>/', views.static_data_import_db, name='static_data_import_db'),
    path('leadership_slogan_analysis/<int:id>/', views.leadership_slogan_analysis, name='leadership_slogan_analysis'),
    path('docs_clause_extractor/<int:id>/', views.docs_clause_extractor, name='docs_clause_extractor'),
    path('docs_approval_reference_extractor/<int:id>/', views.docs_approval_reference_extractor,
         name='docs_approval_reference_extractor'),
    path('docs_definitions_extractor/<int:id>/', views.docs_definitions_extractor, name='docs_definitions_extractor'),
    path('docs_subject_extractor/<int:id>/', views.docs_subject_extractor, name='docs_subject_extractor'),
    path('docs_actors_extractor/<int:id>/', views.docs_actors_extractor, name='docs_actors_extractor'),
    path('docs_lda_topic_extraction/<int:id>/', views.docs_lda_topic_extraction, name='docs_lda_topic_extraction'),
    path('template_panels_data_import_db/<int:id>/', views.template_panels_data_import_db,
         name='template_panels_data_import_db'),

    path('docs_general_actors_extractor/<int:id>/', views.docs_general_actors_extractor,
         name='docs_general_actors_extractor'),
    path('docs_general_definitions_extractor/<int:id>/', views.docs_general_definitions_extractor,
         name='docs_general_definitions_extractor'),

    path('operators_static_data_to_db/<int:id>/', views.operators_static_data_to_db,
         name='operators_static_data_to_db'),
    path('search_parameters_to_db/<int:id>/', views.search_parameters_to_db, name='search_parameters_to_db'),
    path('rahbari_search_parameters_to_db/<int:id>/', views.rahbari_search_parameters_to_db, name='rahbari_search_parameters_to_db'),

    path('create_judgments_table/<int:id>/', views.create_judgments_table, name='create_judgments_table'),
    path('create_standards_table/<int:id>/', views.create_standards_table, name='create_standards_table'),
    path('FindSubjectComplaint/<int:id>/', views.FindSubjectComplaint, name='FindSubjectComplaint'),

    path('docs_opertators_extractor/<int:id>/', views.docs_opertators_extractor, name='docs_opertators_extractor'),

    path('docs_regulators_extractor/<int:id>/', views.docs_regulators_extractor, name='docs_regulators_extractor'),

    path('collective_static_data_to_db/<int:id>/', views.collective_static_data_to_db,
         name='collective_static_data_to_db'),

    path('docs_collective_extractor/<int:id>/', views.docs_collective_extractor, name='docs_collective_extractor'),

    path('docs_complete_para_extractor/<int:id>/', views.docs_complete_para_extractor,
         name='docs_complete_para_extractor'),

    # path('executive_clause_extractor/<int:id>/', views.executive_clause_extractor, name='executive_clause_extractor'),

    path('document_json_list/<int:id>/', views.document_json_list, name='document_json_list'),

    path('actors_static_data_to_db/<int:id>/', views.actors_static_data_to_db, name='actors_static_data_to_db'),
    path('regulators_static_import_db/<int:id>/', views.regulators_static_import_db,
         name='regulators_static_import_db'),
    path('actors_time_series_extractor/<int:id>/', views.actors_time_series_extractor,
         name='actors_time_series_extractor'),

    path('rahbari_labels_time_series_extractor/<int:id>/', views.rahbari_labels_time_series_extractor,
         name='rahbari_labels_time_series_extractor'),

    path('actors_graph_extractor/<int:id>/', views.actors_graph_extractor, name='actors_graph_extractor'),
    path('actors_new_graph_extractor/<int:id>/', views.actors_new_graph_extractor, name='actors_new_graph_extractor'),

    path('create_CUBE_docs_general_actors_extractorubject_Statistics/<int:id>/', views.create_CUBE_Subject_Statistics,
         name='create_CUBE_Subject_Statistics'),
    path('create_CUBE_Subject/<int:id>/', views.create_CUBE_Subject, name='create_CUBE_Subject'),
    path('create_CUBE_CollectiveActor/<int:id>/', views.create_CUBE_CollectiveActor,
         name='create_CUBE_CollectiveActor'),
    path('create_CUBE_RegularityLifeCycle/<int:id>/', views.create_CUBE_RegularityLifeCycle,
         name='create_CUBE_RegularityLifeCycle'),
    path('create_CUBE_MandatoryRegulations/<int:id>/', views.create_CUBE_MandatoryRegulations,
         name='create_CUBE_MandatoryRegulations'),
    path('create_CUBE_Votes/<int:id>/', views.create_CUBE_Votes, name='create_CUBE_Votes'),
    path('create_CUBE_Template/<int:id>/<str:panel_name>/', views.create_CUBE_Template, name='create_CUBE_Template'),

    path('create_CUBE_Principles/<int:id>/', views.create_CUBE_Principle, name='create_CUBE_Principle'),
    path('create_CUBE_MaxMinEffectActorsInArea/<int:id>/', views.create_CUBE_MaxMinEffectActorsInArea,
         name='create_CUBE_MaxMinEffectActorsInArea'),

    path('create_CUBE_BusinessAdvisor/<int:id>/', views.create_CUBE_BusinessAdvisor,
         name='create_CUBE_BusinessAdvisor'),

    path('GetGraphNodesEdges/<int:country_id>/<int:measure_id>/<str:minimum_weight>/', views.GetGraphNodesEdges,
         name='GetGraphNodesEdges'),

    # main pages urls
    path('GetUnknownDocuments/', views.GetUnknownDocuments, name='GetUnknownDocuments'),
    path('DownloadUnknownDocuments/', views.DownloadUnknownDocuments, name='DownloadUnknownDocuments'),
    path('information/', views.information, name='information'),
    path('information3/', views.information3, name='information3'),
    path('following_document_comments/', views.following_document_comments, name='following_document_comments'),
    path('notes/', views.notes, name='notes'),
    path('approvals_terminology/', views.approvals_terminology, name='approvals_terminology'),
    path('judge_dashboard/', views.judge_dashboard, name='judge_dashboard'),
    path('get_judge_profile_data/<int:judge_id>/', views.get_judge_profile_data, name='get_judge_profile_data'),
    path('get_all_judges/', views.get_all_judges, name='get_all_judges'),
    path('get_judge_dashboard_data/', views.get_judge_dashboard_data, name='get_judge_dashboard_data'),
    path('specific_judge_profile/', views.specific_judge_profile, name='specific_judge_profile'),
    #     path('judge_behavior_analysis', views.judge_behavior_analysis, name='judge_behavior_analysis'),
    path('GetAllNotesUser/<str:username>/', views.GetAllNotesUser, name='GetAllNotesUser'),
    path('graph/', views.graph, name='graph'),
    path('graph2/', views.graph2, name='graph2'),
    path('search/', views.search, name='search'),
    path('es_search/', views.es_search, name='es_search'),
    path('dendrogram/<int:country_id>/<str:ngram_type>/', views.dendrogram, name='dendrogram'),
    path('decision_tree/<int:country_id>/<int:clustering_algorithm_id>/', views.decision_tree, name='decision_tree'),
    path('judgment_search/', views.judgment_search, name='judgment_search'),
    path('judgment_validation/', views.judgment_search, name='judgment_validation'),
    path('rahbari_search/', views.rahbari_search, name='rahbari_search'),
    path('rahbari_paraghraph/', views.rahbari_paraghraph, name='rahbari_paraghraph'),
    path('rahbari_subject/', views.rahbari_subject, name='rahbari_subject'),
    path('rahbari_organization/', views.rahbari_organization, name='rahbari_organization'),
    path('rahbari_problem_system/', views.rahbari_problem_system, name='rahbari_problem_system'),
    path('rahbari_topic/', views.rahbari_topic, name='rahbari_topic'),
    path('rahbari_labels/', views.rahbari_labels, name='rahbari_labels'),
    path('subject/', views.subject, name='subject'),
    path('subject_statistics/', views.subject_statistics, name='subject_statistics'),
    path('votes_analysis/', views.votes_analysis, name='votes_analysis'),
    path('leadership_slogan/', views.leadership_slogan, name='leadership_slogan'),
    path('adaptation/', views.adaptation, name='adaptation'),
    path('comparison/', views.comparison, name='comparison'),
    path('adaptation_comparison/<int:country_id>/<int:document_id>/<str:draft_name>/<str:searched_keywords>/',
         views.adaptation_comparison, name='adaptation_comparison'),
    path('subject_graph/', views.subject_graph, name='subject_graph'),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/<str:email>/", views.forgot_password_by_email, name="forgot_password_by_email"),
    path("reset-password/<str:user_id>/<str:token>", views.reset_password_check, name="reset_password_check"),
    path("reset-password/<str:user_id>/<str:token>/<str:password>", views.reset_password, name="reset_password"),
    path("admin/", views.Admin, name="admin"),
    path("manage_users_tab/", views.ManageUsersTab, name="manage_users_tab"),
    path("manage_users/", views.ManageUsers, name="manage_users"),
    path("get_access_to_all_users/", views.GetAcceseToAllUsers, name="get_access_to_all_users"),
    path("GetSyns/", views.GetSyns, name="GetSyns"),
    path("get_permissions_excel/", views.GetPermissionsExcel, name="get_permissions_excel"),
    path("get_allowed_panels/", views.GetAllowedPanels, name="get_allowed_panels"),
    path("get_allowed_panels/<str:username>/", views.GetPermissions, name="get_allowed_panels_by_username"),
    path("get_all_panels/", views.GetAllPanels, name="get_allowed_panels_by_username"),
    path("create_panels/", views.CreatePanel, name="create_panels"),
    path("create_or_delete_user_panels/<str:panel_name>/<str:username>/", views.CreateOrDeleteUserPanel,
         name="create_or_delete_user_panels"),
    path("admin_waiting_user/", views.getRegisteredUser, name="admin_waiting_user"),
    path("admin_confirm_waiting_user/", views.getRegisteredUser2, name="admin_confirm_waiting_user"),
    path("admin_accepted_user/", views.seeAcceptedUser, name="admin_accepted_user"),
    path("super_admin_user_log/", views.showUserLogs, name="super_admin_user_log"),
    path("deploy_server_log/", views.showDeployLogs, name="deploy_server_log"),
    path("admin_user_recommendation/", views.get_user_recommendation, name="admin_user_recommendation"),
    path("admin_user_report_bug/", views.get_user_report_bug, name="admin_user_report_bug"),
    path("admin_accept_user_comments/", views.seeAllComment, name="admin_accept_user_comments"),
    path("admin_confirm_user_comments/", views.seeAllComment2, name="admin_confirm_user_comments"),
    path("admin_upload/", views.admin_upload, name="admin_upload"),
    path("admin_book_upload/", views.admin_book_upload, name="admin_book_upload"),
    path("pdf2text/", views.pdf2text, name="pdf2text"),
    path("regularity/", views.regularity, name="regularity"),
    path("regularity_life_cycle/", views.regularity_life_cycle, name="regularity_life_cycle"),
    path('definition/', views.definition, name='definition'),
    path("business_advisor/", views.business_advisor, name='business_advisor'),
    path("executive_regulations_analysis/", views.executive_regulations_analysis,
         name='executive_regulations_analysis'),
    path("executive_regulations_analysis_v2/", views.executive_regulations_analysis2,
         name='executive_regulations_analysis_v2'),
    path("executive_regulations_analysis_v3/", views.executive_regulations_analysis3,
         name='executive_regulations_analysis_v3'),
    path("revoked_document/", views.revoked_document, name='revoked_document'),
    path("revoked_document2/", views.revoked_document2, name='revoked_document2'),

    path("window_unit/", views.window_unit, name='window_unit'),
    path("collective_actors/", views.collective_actors, name='collective_actors'),
    path("collective_actors_es/", views.collective_actors_es, name='collective_actors_es'),
    path("official_references/", views.official_references, name='official_references'),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('report_bug/', views.report_bug, name='report_bug'),
    path("future_work/", views.future_work, name='future_work'),
    path("principles_analysis/", views.principles_analysis, name='principles_analysis'),
    path("portal/", views.portal, name='portal'),
    path("actors_information/", views.actors_information, name='actors_information'),
    # path("actors_search/", views.actors_search, name='actors_search'),
    path("actors_search/", views.actors_search_es, name='actors_search'),
    path("actors_graph/", views.actors_graph, name='actors_graph'),
    path("actors_agile/", views.actors_agile, name='actors_agile'),
    path("approvals_list/", views.approvals_list, name='approvals_list'),
    path("document_validation/", views.document_validation, name='document_validation'),
    path("approvals_adaptation/", views.approvals_adaptation, name='approvals_adaptation'),
    path("legal_literature_adaptation/", views.legal_literature_adaptation, name="legal_literature_adaptation"),
    path("Cancellationـanalysis/", views.Cancellationـanalysis, name='Cancellationـanalysis'),
    path("compare_document/", views.compare_document, name='compare_document'),

    path('judgement_graph/', views.judgement_graph, name='judgement_graph'),
    path('GetJudgementTypeByCountryId/<int:country_id>/', views.GetJudgementTypeByCountryId,
         name='GetJudgementTypeByCountryId'),
    path('GetJudgementGraphNodesEdges/<int:country_id>/<str:selected_type>/', views.GetJudgementGraphNodesEdges,
         name='GetJudgementGraphNodesEdges'),

    path('book_analysis/', views.book_analysis, name='book_analysis'),

    # books v2
    path('submit_book_informations/', views.submit_book_informations, name='submit_book_informations'),
    path('admin_submit_book_informations/', views.admin_submit_book_informations,
         name='admin_submit_book_informations'),
    path('book_requests/', views.book_requests, name='book_requests'),
    path('book_information/', views.book_information, name='book_information'),
    path('book_search/', views.book_search, name='book_search'),
    path('book_graph/', views.book_graph, name='book_graph'),
    path('book_disagreement_with_rules/', views.book_disagreement_with_rules, name='book_disagreement_with_rules'),
    path('flow_detection/', views.flow_detection, name='flow_detection'),
    path('GetBookSimilarityMeasureByCountry/<int:country_id>/', views.GetBookSimilarityMeasureByCountry,
         name='GetBookSimilarityMeasureByCountry'),
    path('GetBookGraphDistribution/<int:country_id>/<int:measure_id>/', views.GetBookGraphDistribution,
         name='GetBookGraphDistribution'),
    path('GetBookGraphNodesEdges/<int:country_id>/<int:measure_id>/<str:minimum_weight>/', views.GetBookGraphNodesEdges,
         name='GetBookGraphNodesEdges'),
    path('get_all_books/', views.get_all_books, name='get_all_books'),
    path('submit_book_info_by_publisher/<int:book_id>/', views.submit_book_info_by_publisher,
         name='submit_book_info_by_publisher'),
    path('submit_book_info_by_admin/<int:book_id>/<str:publishername>/<str:book_subject>/<str:year>/<str:pagecount>/',
         views.submit_book_info_by_admin, name='submit_book_info_by_admin'),
    path('get_book_by_status/<str:status>/', views.get_book_by_status, name='get_book_by_status'),
    path('ChangebookStatus/<int:book_id>/<str:status>/', views.ChangebookStatus, name='ChangebookStatus'),
    path('GetSimilarity/<int:document_id>/', views.GetSimilarity, name='GetSimilarity'),
    path("delete_user/<int:user_id>/", views.DeleteUser, name='DeleteUser'),
    path('GetParagraphSimilarity/<int:document_id>/<int:curr_document_id>/', views.GetParagraphSimilarity,
         name='GetParagraphSimilarity'),

    path('GetBM25Similarity/<int:document_id>/', views.GetBM25Similarity, name='GetBM25Similarity'),
    path('GetSimilarParagraphs_ByParagraphID/<int:paragraph_id>/', views.GetSimilarParagraphs_ByParagraphID, name='GetSimilarParagraphs_ByParagraphID'),


    # standard
    path('standard_information/', views.standard_information, name='standard_information'),
    path('standard_search/', views.standard_search, name='standard_search'),
    path('standard_graph/', views.standard_graph, name='standard_graph'),
    path("admin_standard_upload/", views.admin_standard_upload, name="admin_standard_upload"),
    path('GetStandardDocumentById/<int:document_id>/', views.GetStandardDocumentById, name="GetStandardDocumentById"),
    path('GetStandardsSearchParameters/<int:country_id>/', views.GetStandardsSearchParameters,
         name="GetStandardsSearchParameters"),
    path(
        'SearchDocument_ES_Standard/<int:country_id>/<int:branch>/<int:subject_category>/<int:status>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/<str:search_type>/',
        views.SearchDocument_ES_Standard, name='SearchDocument_ES_Standard'),
    path('standard_graph_v2/', views.standard_graph_v2, name='standard_graph_v2'),
    path('GetStandardTypeByCountryId/<int:country_id>/', views.GetStandardTypeByCountryId,
         name='GetStandardTypeByCountryId'),
    path('GetStandardGraphNodesEdges/<int:country_id>/<str:selected_type>/', views.GetStandardGraphNodesEdges,
         name='GetStandardGraphNodesEdges'),

    # urls inside main pages
    path('GetDocumentById/<int:id>/', views.GetDocumentById, name='GetDocumentById'),
    path('get_judgment_subject_type_display_name/<str:name>/', views.get_judgment_subject_type_display_name,
         name='get_judgment_subject_type_display_name'),
    path('GetBookDocumentById/<int:document_id>/', views.GetBookDocumentById, name='GetBookDocumentById'),
    path('GetDocumentsByCountryId_Modal/<int:country_id>/<int:start_index>/<int:end_index>/',
         views.GetDocumentsByCountryId_Modal, name='GetDocumentsByCountryId_Modal'),
    path('GetDocumentsByCountrySubject/<int:country_id>/<str:subjects_id>/', views.GetDocumentsByCountrySubject,
         name='GetDocumentsByCountrySubject'),
    path('GetDocumentsByCountrySubject_ES/<int:curr_page>/<int:country_id>/<str:subjects_ids>/',
         views.GetDocumentsByCountrySubject_ES, name='GetDocumentsByCountrySubject_ES'),
    path('GetDocumentsWithoutSubject/<int:country_id>/<int:measure_id>/', views.GetDocumentsWithoutSubject,
         name='GetDocumentsWithoutSubject'),
    path('GetDocumentsWithoutSubject_ES/<int:curr_page>/<int:country_id>/', views.GetDocumentsWithoutSubject_ES,
         name='GetDocumentsWithoutSubject_ES'),
    path('GetCountryById/<int:id>/', views.GetCountryById, name='GetCountryById'),
    path('GetTFIDFByDocumentId/<int:document_id>/', views.GetTFIDFByDocumentId, name='GetTFIDFByDocumentId'),
    path('GetTFIDFByDocumentId/<int:document_id>/', views.GetTFIDFByDocumentId, name='GetTFIDFByDocumentId'),
    path('get_TFIDF_similarity_for_2_document/<int:document1>/<int:document2>/',
         views.get_TFIDF_similarity_for_2_document, name='get_TFIDF_similarity_for_2_document'),
    path('get_similarity_for_2_document/<int:doc_id_1>/<int:doc_id_2>/<str:measure>/',
         views.get_similarity_for_2_document, name='get_similarity_for_2_document'),
    path('GetDefinitionByDocumentId/<int:document_id>/', views.GetDefinitionByDocumentId,
         name='GetDefinitionByDocumentId'),
    path('GetPersianDefinitionByDocumentId/<int:document_id>/', views.GetPersianDefinitionByDocumentId,
         name='GetPersianDefinitionByDocumentId'),
    path('GetNGramByDocumentId/<int:document_id>/<int:gram>/', views.GetNGramByDocumentId, name='GetNGramByDocumentId'),
    path('GetReferencesByDocumentId/<int:document_id>/<int:type>/', views.GetReferencesByDocumentId,
         name='GetReferencesByDocumentId'),
    path('GetSubjectByDocumentId/<int:document_id>/<int:measure_id>/', views.GetSubjectByDocumentId,
         name='GetSubjectByDocumentId'),
    path('GetGraphSimilarityMeasureByCountry/<int:country_id>/', views.GetGraphSimilarityMeasureByCountry,
         name='GetGraphSimilarityMeasureByCountry'),
    path('GetGraphDistribution/<int:country_id>/<int:measure_id>/', views.GetGraphDistribution,
         name='GetGraphDistribution'),
    path('GetSubjectsByCountryId/<int:country_id>/', views.GetSubjectsByCountryId, name='GetSubjectsByCountryId'),
    path('GetSubjectKeywords/<int:subject_id>/', views.GetSubjectKeywords, name='GetSubjectKeywords'),
    path('GetCommonWords2Doc/<int:document1_id>/<int:document2_id>/', views.GetCommonWords2Doc,
         name='GetCommonWords2Doc'),
    path('GetReferences2Doc/<int:document1_id>/<int:document2_id>/', views.GetReferences2Doc, name='GetReferences2Doc'),
    path('GetTypeByCountryId/<int:country_id>/', views.GetTypeByCountryId, name='GetTypeByCountryId'),
    path('GetLevelByCountryId/<int:country_id>/', views.GetLevelByCountryId, name='GetLevelByCountryId'),
    path('GetApprovalReferencesByCountryId/<int:country_id>/', views.GetApprovalReferencesByCountryId,
         name='GetApprovalReferencesByCountryId'),
    path('GetYearsBoundByCountryId/<int:country_id>/', views.GetYearsBoundByCountryId, name='GetYearsBoundByCountryId'),
    path('GetDocumentByCountryTypeSubject_Modal/<int:country_id>/<int:type_id>/<int:subject_id>/<str:tag>/',
         views.GetDocumentByCountryTypeSubject_Modal, name='GetDocumentByCountryTypeSubject_Modal'),
    path('GetDocumentByCountryTypeSubject/<int:country_id>/<int:type_id>/<int:subject_id>/<str:tag>/',
         views.GetDocumentByCountryTypeSubject, name='GetDocumentByCountryTypeSubject'),
    path(
        'GetGraphEdgesByDocumentIdMeasure/<int:country_id>/<int:src_doc_id>/<int:src_type_id>/<int:src_subject_id>/<int:dest_doc_id>/<int:dest_type_id>/<int:dest_subject_id>/<int:measure_id>/<str:weight>/',
        views.GetGraphEdgesByDocumentIdMeasure, name='GetGraphEdgesByDocumentIdMeasure'),
    path('GetGraphEdgesByDocumentsList/<int:measure_id>/', views.GetGraphEdgesByDocumentsList,
         name='GetGraphEdgesByDocumentsList'),
    path('GetGraphEdgesForDocument/<int:measure_id>/<int:document_id>/', views.GetGraphEdgesForDocument,
         name='GetGraphEdgesForDocument'),
    path(
        'SearchDocumentOR/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/',
        views.SearchDocumentOR, name='SearchDocumentOR'),
    path(
        'SearchDocumentAnd/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/',
        views.SearchDocumentAnd, name='SearchDocumentAnd'),

    path(
        'SearchDocumentExact/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/',
        views.SearchDocumentExact, name='SearchDocumentExact'),
    path(
        'SearchDocument_ES/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchDocument_ES, name='SearchDocument_ES'),
    path(
        'SearchDocuments_Column_ES/<int:country_id>/<str:level_name>/<str:subject_name>/<str:type_name>/<str:approval_reference_name>/<str:from_year>/<str:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<str:revoked_type_name>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchDocuments_Column_ES, name='SearchDocuments_Column_ES'),
    path(
        'SearchDocumentsValidation_Column_ES/<int:country_id>/<str:level_name>/<str:subject_area_name>/<str:subject_sub_area_name>/<str:type_name>/<str:approval_reference_name>/<str:from_year>/<str:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<str:revoked_type_name>/<str:revoke_type_detail>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchDocumentsValidation_Column_ES, name='SearchDocumentsValidation_Column_ES'),

    path(
        'Get_Documents_RefGraph_ES/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.Get_Documents_RefGraph_ES, name='Get_Documents_RefGraph_ES'),

    path(
        'SearchDocumentSubjectArea_ES/<int:country_id>/<str:revoked_type_id>/<str:subject_area_name>/<str:subject_sub_area_name>/<str:organization_name>/<int:type_id>/<str:revoked_size>/<str:place>/<str:text>/<str:search_type>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:curr_page>/',
        views.SearchDocumentSubjectArea_ES, name='SearchDocumentSubjectArea_ES'),
    path(
        'approvalsList_ES/<int:country_id>/<int:level_id>/<str:subject_area_name>/<str:subject_sub_area_name>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:organization_type_id>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.approvalsList_ES, name='approvalsList_ES'),

    path(
        'approvalsList_RefGraph_ES/<int:country_id>/<int:level_id>/<str:subject_area_name>/<str:subject_sub_area_name>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:organization_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.approvalsList_RefGraph_ES, name='approvalsList_RefGraph_ES'),

    path(
        'approvalsList_ES_2/<int:country_id>/<int:level_id>/<str:subject_area_text>/<str:subject_sub_area_text>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:revoke_type_detail>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.approvalsList_ES_2, name='approvalsList_ES_2'),
    path('SearchDocument_ES_web/<str:text>/', views.SearchDocument_ES_web, name='SearchDocument_ES_web'),
    path(
        'SearchJudgment_ES/<int:country_id>/<int:JudgeName>/<int:SubjectTypeDisplayName>/<int:JudgmentType>/<int:Categories>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchJudgment_ES, name='SearchJudgment_ES'),
    path(
        'SearchDocument_ES2/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.SearchDocument_ES2, name='SearchDocument_ES2'),
    path(
        'SearchDocument_ES_Book/<int:country_id>/<str:subject>/<str:publisher_name>/<str:place>/<str:text>/<str:search_type>/',
        views.SearchDocument_ES_Book, name='SearchDocument_ES_Book'),
    path('GetActorsChartData_ES/<str:text>/<str:doc_ids_text>/', views.GetActorsChartData_ES,
         name='GetActorsChartData_ES'),
    path(
        'GetActorsChartData_ES_2/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.GetActorsChartData_ES_2, name='GetActorsChartData_ES_2'),

    path('GetSearchDetails_ES/<int:document_id>/<str:search_type>/<str:text>/', views.GetSearchDetails_ES,
         name='GetSearchDetails_ES'),

    path('GetSearchDetails_ES_2/<int:document_id>/<str:search_type>/<str:text>/', views.GetSearchDetails_ES_2,
         name='GetSearchDetails_ES_2'),

    path('GetSearchDetails_ES_Judgment/<int:document_id>/<str:search_type>/<str:text>/',
         views.GetSearchDetails_ES_Judgment, name='GetSearchDetails_ES_Judgment'),
    path('SearchGeneralDefinitions_ES/<int:country_id>/<str:type>/<int:is_term>/<int:curr_page>/<str:text>/',
         views.SearchGeneralDefinitions_ES, name='SearchGeneralDefinitions_ES'),

    path('advisory_opinions_analysis/', views.advisory_opinions_analysis, name='advisory_opinions_analysis'),
    path('advisory_opinions_analysis2/', views.advisory_opinions_analysis2, name='advisory_opinions_analysis2'),
    path('GetAdvisoryOpinionsReferencesByDocumentId/<str:doc_id>/', views.GetAdvisoryOpinionsReferencesByDocumentId,
         name='GetAdvisoryOpinionsReferencesByDocumentId'),
    path('GetAdvisoryChartInformation/<str:doc_id>/', views.GetAdvisoryChartInformation,
         name='GetAdvisoryChartInformation'),
    path('GetAdvisoryDetail_ES/<str:doc_id>/<int:curr_page>/', views.GetAdvisoryDetail_ES,
         name='GetAdvisoryDetail_ES'),    
    path('GetAdvisoryChartInformation_ES/<str:doc_id>/<str:subject_name>/<str:from_year>/<str:to_year>/<str:approval_reference_name>/<int:curr_page>/',
          views.GetAdvisoryChartInformation_ES, name='GetAdvisoryChartInformation_ES'),
         
    path('GetAreaChartInformation/<str:doc_id>/', views.GetAreaChartInformation, name='GetAdvisoryChartInformation'),
    path('GetGraphEdgesByDocumentsList_AdvisoryOpinions/<int:measure_id>/',
         views.GetGraphEdgesByDocumentsList_AdvisoryOpinions, name='GetGraphEdgesByDocumentsList_AdvisoryOpinions'),
    path('create_advisory_opinion_count/<int:id>/<str:language>/', views.create_advisory_opinion_count,
         name='create_advisory_opinion_count'),
    path('create_interpretation_rules_count/<int:id>/<str:language>/', views.create_interpretation_rules_count,
         name='create_interpretation_rules_count'),
    path('GetSearchParameters/<int:country_id>/', views.GetSearchParameters, name='GetSearchParameters'),
    path('GetJudgmentSearchParameters/<int:country_id>/', views.GetJudgmentSearchParameters,
         name='GetJudgmentSearchParameters'),
    path('GetBooksSearchParameters/<int:country_id>/', views.GetBooksSearchParameters, name='GetBooksSearchParameters'),
    path('GetRahbariSearchParameters/<int:country_id>/', views.GetRahbariSearchParameters,
         name='GetRahbariSearchParameters'),
    path('interpretation_rules_analysis/', views.interpretation_rules_analysis, name='interpretation_rules_analysis'),
    
    path('SearchRahbari_ES/<int:country_id>/<int:type_id>/<str:label_name>/<int:from_year>/<int:to_year>/<str:rahbari_type>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/<int:search_result_size>/',
        views.SearchRahbari_ES, name='SearchRahbari_ES'),

    path(
        'SearchRahbariRule_ES/<int:country_id>/<int:type_id>/<str:label_name>/<int:from_year>/<int:to_year>/<str:rahbari_type>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchRahbariRule_ES, name='SearchRahbariRule_ES'),

    path(
        'Search_Rahbari_Column_ES/<int:country_id>/<str:type_name>/<str:label_name_list>/<str:from_year>/<str:to_year>/<str:rahbari_type>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.Search_Rahbari_Column_ES, name='Search_Rahbari_Column_ES'),

    path(
        'Search_Rahbari_Paragraph_Column_ES/<int:country_id>/<str:type_name>/<str:label_name_list>/<str:from_year>/<str:to_year>/<str:place>/<str:text>/<str:search_type>/<str:field_name>/<str:field_value>/<str:sentiment>/<int:curr_page>/<int:result_size>/',
        views.Search_Rahbari_Paragraph_Column_ES, name='Search_Rahbari_Paragraph_Column_ES'),

    path(
        'Export_Rahbari_Paragraph_Column_ES/<int:country_id>/<str:type_name>/<str:label_name_list>/<str:from_year>/<str:to_year>/<str:place>/<str:text>/<str:search_type>/<str:field_name>/<str:field_value>/<str:sentiment>/<int:curr_page>/<int:result_size>/',
        views.Export_Rahbari_Paragraph_Column_ES, name='Export_Rahbari_Paragraph_Column_ES'),

    path(
        'SearchDocumentWithoutText/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/',
        views.SearchDocumentWithoutText, name='SearchDocumentWithoutText'),
    path('SearchDocumentByname/<int:country_id>/<str:text>/', views.SearchDocumentByname, name='SearchDocumentByname'),
    path('GetSearchDetailsAndOR/<int:document_id>/<str:text>/<str:where>/<str:mode>/', views.GetSearchDetailsAndOR,
         name='GetSearchDetailsAndOR'),

    path('GetSearchDetailsExact/<int:document_id>/<str:text>/<str:where>/', views.GetSearchDetailsExact,
         name='GetSearchDetailsExact'),

    path('GetTypeByName/<str:name>/', views.GetTypeByName, name='GetTypeByName'),
    path('GetDocumentsByCountryType_Modal/<int:country_id>/<int:type_id>/', views.GetDocumentsByCountryType_Modal,
         name='GetDocumentsByCountryType_Modal'),
    path('GetSelectedAraDetails/<str:documents_id>/', views.GetSelectedAraDetails, name='GetSelectedAraDetails'),
    path('GetKeywordsDetailsExact/<int:document_id>/<str:text>/', views.GetKeywordsDetailsExact,
         name='GetKeywordsDetailsExact'),
    path('UploadDraft/', views.UploadDraft, name='UploadDraft'),
    path('GetActorsList/', views.GetActorsList, name='GetActorsList'),
    path('GetActorsDict/', views.GetActorsDict, name='GetActorsDict'),

    path('GetDocActorParagraphs_Column_Modal/<int:document_id>/<str:actor_name>/<str:role_name>/',
         views.GetDocActorParagraphs_Column_Modal, name='GetDocActorParagraphs_Column_Modal'),

    path('follow/<str:follower_username>/<int:following_user_id>/', views.follow, name='follow'),
    path('unfollow/<str:follower_username>/<int:following_user_id>/', views.unfollow, name='unfollow'),
    path('GetFollowings/<str:follower_username>/', views.GetFollowings, name='GetFollowings'),
    path('GetUserComments/<int:user_id>/<int:hashtag_id>/', views.GetUserComments, name='GetUserComments'),

    path('GetAllUsers_Commented/<str:user_name>/<str:user_type>/', views.GetAllUsers_Commented,
         name='GetAllUsers_Commented'),

    path('UpdateNgramScore/<int:document_id>/<int:gram>/<str:gram_ids>/', views.UpdateNgramScore,
         name='UpdateNgramScore'),
    path('InsertNgram/<int:document_id>/<int:gram>/<str:texts>/', views.InsertNgram, name='InsertNgram'),
    path('DeleteNgram/<int:gram_id>/', views.DeleteNgram, name='DeleteNgram'),
    path('GetActorsPararaphsByDocumentId/<int:document_id>/', views.GetActorsPararaphsByDocumentId,
         name='GetActorsPararaphsByDocumentId'),
    path('GetActorsKeywordsGraphByDocumentsIdKeywords/<str:document_ids_text>/<str:keywords_text>/',
         views.GetActorsKeywordsGraphByDocumentsIdKeywords, name='GetActorsKeywordsGraphByDocumentsIdKeywords'),
    path(
        'GetActorParaphraphsByDocumentsIdActorNameKeyword_Modal/<str:documents_id_text>/<str:actor_name>/<str:keyword>/',
        views.GetActorParaphraphsByDocumentsIdActorNameKeyword_Modal,
        name='GetActorParaphraphsByDocumentsIdActorNameKeyword_Modal'),
    path('getDraftActors/<int:country_id>/<str:draft_name>/', views.getDraftActors, name='getDraftActors'),
    path('SearchDocumentsByWindowUnit/<int:country_id>/', views.searchDocumentsByWindowUnit,
         name='SearchDocumentsByWindowUnit'),
    path('GetWindowUnitParagraphsDetails/<int:document_id>/', views.GetWindowUnitParagraphsDetails,
         name='GetWindowUnitParagraphsDetails'),
    path('GetCollectiveActorsParagraphsDetails/<int:document_id>/<str:collective_actor_name>/',
         views.GetCollectiveActorsParagraphsDetails, name='GetCollectiveActorsParagraphsDetails'),
    path('GetParagraphReferences/<int:paragraph_id>/', views.GetParagraphReferences,
         name='GetParagraphReferences'),
    path('GetParagraphDefinitions/<int:document_id>/<int:paragraph_id>/', views.GetParagraphDefinitions,
         name='GetParagraphDefinitions'),
    path('searchDocumentsByWindowUnitKeyword/<int:country_id>/<str:keyword>/', views.searchDocumentsByWindowUnitKeyword,
         name='searchDocumentsByWindowUnitKeyword'),
    path('GetDocumentContent/<int:document_id>/', views.GetDocumentContent, name='GetDocumentContent'),
    path('GetDocumentSubjectContent/<int:document_id>/<int:version_id>/', views.GetDocumentSubjectContent,
         name='GetDocumentSubjectContent'),
    path('GetSubjectSubjectGraphData/<int:country_id>/<int:version_id>/', views.GetSubjectSubjectGraphData,
         name='GetSubjectSubjectGraphData'),

    path('SearchGeneralDocumentsDefinition/<int:country_id>/<str:mode>/<str:text>/',
         views.SearchGeneralDocumentsDefinition, name='SearchGeneralDocumentsDefinition'),
    path('GetKeywordsGeneralDefinitionByDocumentId/<int:document_id>/<str:word>/',
         views.GetKeywordsGeneralDefinitionByDocumentId, name='GetKeywordsGeneralDefinitionByDocumentId'),

    path(
        'SaveUser/<str:firstname>/<str:lastname>/<str:nationalcode>/<str:email>/<str:phonenumber>/<int:role>/<str:username>/<str:password>/<str:ip>/<str:expertise>/',
        views.SaveUser, name='SaveUser'),
    path('CheckUserLogin/<str:username>/<str:password>/<str:ip>/', views.CheckUserLogin, name='CheckUserLogin'),
    path('changeUserState/<int:user_id>/<str:state>/', views.changeUserState, name='changeUserState'),
    path('changeCommentState/<int:comment_id>/<str:state>/', views.changeCommentState, name='changeCommentState'),
    path('GetDocumentCommentVoters/<int:document_comment_id>/<str:agreed>/', views.GetDocumentCommentVoters,
         name='GetDocumentCommentVoters'),

    path('GetUserRole/', views.GetUserRole, name='GetUserRole'),
    path('GetUserExpertise/', views.GetUserExpertise, name='GetUserExpertise'),
    path('UploadCompressedPdfs/', views.UploadCompressedPdfs, name='UploadCompressedPdfs'),
    path('DownloadPdfTexts/', views.DownloadPdfTexts, name='DownloadPdfTexts'),
    path('UserLogSaved/<str:username>/<str:url>/<str:ip>/', views.UserLogSaved, name='UserLogSaved'),
    path('UserDeployLogSaved/<str:username>/<str:detail>/', views.UserDeployLogSaved, name='UserDeployLogSaved'),
    path('GetMandatoryRegulations/<int:country_id>/', views.GetMandatoryRegulations, name='GetMandatoryRegulations'),
    path('CompareRegulatorAndLaw/<int:regulator_id>/', views.CompareRegulatorAndLaw, name='CompareRegulatorAndLaw'),
    path('GetNextParagraph/<int:paragraph_id>/', views.GetNextParagraph, name='GetNextParagraph'),

    path('Recommendations/<str:first_name>/<str:last_name>/<str:email>/<str:recommendation_text>/<int:rating_value>/',
         views.Recommendations, name='Recommendations'),

    path('CreateDocumentComment/<int:document>/<str:comment>/<str:username>/<str:comment_show_info>/<str:time>/',
         views.CreateDocumentComment, name='CreateDocumentComment'),
    path('CreateHashTagForDocumentComment/<int:comment_id>/<str:hash_tag>/', views.CreateHashTagForDocumentComment,
         name='CreateHashTagForDocumentComment'),
    path('GetAllUserCommentHashtags/', views.GetAllUserCommentHashtags, name='GetAllUserCommentHashtags'),

    #     path('Report_Bugs/<str:username>/<str:report_bug_text>/<str:panel_name>/', views.Report_Bugs, name='Report_Bugs'),
    #     path('ChangeReportBugCheckStatus/<int:report_bug_id>/', views.ChangeReportBugCheckStatus, name='ChangeReportBugCheckStatus'),
    #     path('GetReportBug/', views.GetReportBug, name='GetReportBug'),

    #     path('CreateDocumentComment/<int:document>/<str:comment>/<str:username>/<str:comment_show_info>/', views.CreateDocumentComment, name='CreateDocumentComment'),
    path('CreateReportBug/<str:username>/<str:report_bug_text>/<str:panel_id>/<str:branch_id>/', views.CreateReportBug,
         name='CreateReportBug'),
    path('ChangeReportBugCheckStatus/<int:report_bug_id>/', views.ChangeReportBugCheckStatus,
         name='ChangeReportBugCheckStatus'),
    path('GetReportBugByFilter/<str:panel_id>/<str:branch_id>/<str:status>/', views.GetReportBugByFilter,
         name='GetReportBugByFilter'),
    #     path('CreateDocumentComment/<int:document>/<str:comment>/<str:username>/', views.CreateDocumentComment, name='CreateDocumentComment'),

    path('GetDocumentComments/<int:document>/<str:username>/', views.GetDocumentComments, name='GetDocumentComments'),

    path('CreateDocumentNote/<int:document>/<str:note>/<str:username>/<str:time>/<str:label>/',
         views.CreateDocumentNote, name='CreateDocumentNote'),
    path('CreateHashTagForNote/<int:note_id>/<str:hash_tag>/', views.CreateHashTagForNote, name='CreateHashTagForNote'),
    path('GetDocumentNotes/<int:document>/<str:username>/', views.GetDocumentNotes, name='GetDocumentNotes'),
    path('ToggleNoteStar/<int:note_id>/', views.ToggleNoteStar, name='ToggleNoteStar'),

    path('changeVoteState/<str:username>/<int:document_comment>/<str:state>/', views.changeVoteState,
         name='changeVoteState'),

    # mandatory executive regulations
    path('GetMandatoryRegulations2/<int:country_id>/', views.GetMandatoryRegulations2, name='GetMandatoryRegulations2'),
    path('GetMandatoryRegulationsDetail/<int:regulator_id>/', views.GetMandatoryRegulationsDetail,
         name='GetMandatoryRegulationsDetail'),

    # added for sample_template/portal
    path('UserLogSaved/<str:username>/<str:url>/<str:sub_url>/<str:ip>/', views.UserLogSaved, name='UserLogSaved'),

    path('getUserLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getUserLogs, name='getUserLogs'),
    path('getChartLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getChartLogs, name='getChartLogs'),
    path('getTableUserLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getTableUserLogs,
         name='getTableUserLogs'),
    path('getUserChartLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getUserChartLogs,
         name='getUserChartLogs'),
    path('GetAllNotesInTimeRange/<str:username>/<str:time_start>/<str:time_end>/', views.GetAllNotesInTimeRange,
         name='GetAllNotesInTimeRange'),
    path(
        'GetNotesInTimeRangeFilterLabelHashtag/<str:username>/<str:time_start>/<str:time_end>/<str:label>/<str:hashtag>/',
        views.GetNotesInTimeRangeFilterLabelHashtag, name='GetNotesInTimeRangeFilterLabelHashtag'),

    path('getUserDeployLogs/', views.getUserDeployLogs, name='getUserDeployLogs'),

    path('UploadFile/<str:country>/<str:language>/<str:tasks_list>/', views.UploadFile, name='UploadFile'),
    path('GetMostRepetitiveKeywords/<int:country_id>/<str:subject_ids>/', views.GetMostRepetitiveKeywords,
         name='GetMostRepetitiveKeywords'),
    path('GetKeywordsDefinition/<int:country_id>/<str:word>/', views.GetKeywordsDefinition,
         name='GetKeywordsDefinition'),
    path('SearchDocumentsDefinitionByCountryId/<int:country_id>/<str:subject_ids>/',
         views.SearchDocumentsDefinitionByCountryId, name='SearchDocumentsDefinitionByCountryId'),
    path('GetGeneralDefinition/<int:document_id>/', views.GetGeneralDefinition, name='GetGeneralDefinition'),
    path('GetGeneralDefinition2/<int:document_id>/', views.GetGeneralDefinition2, name='GetGeneralDefinition2'),
    path('GetGeneralDefinitionsByCountry/<int:country_id>/<str:type>/<int:curr_page>/<str:text>/',
         views.GetGeneralDefinitionsByCountry, name='GetGeneralDefinitionsByCountry'),
    path('GetKeywordsActorsGraphData/<int:country_id>/<str:type>/<str:text>/<int:curr_page>/',
         views.GetKeywordsActorsGraphData, name='GetKeywordsActorsGraphData'),
    path('GetKeywordActorsGraphData/<int:country_id>/<str:type>/<str:text>/<int:curr_page>/',
         views.GetKeywordActorsGraphData, name='GetKeywordActorsGraphData'),
    path('SearchDocumentsDefinitionByCountryId/<int:country_id>/', views.SearchDocumentsDefinitionByCountryId,
         name='SearchDocumentsDefinitionByCountryId'),
    path('GetKeywordsDefinitionByDocumentId/<int:document_id>/<str:word>/', views.GetKeywordsDefinitionByDocumentId,
         name='GetKeywordsDefinitionByDocumentId'),
    path('GetLocalTextFile/<str:name>/', views.GetLocalTextFile, name='GetLocalTextFile'),
    path('GetAllKeywords/', views.GetAllKeywords, name='GetAllKeywords'),

    # Collective actor
    path('GetCollectiveActorList/', views.GetCollectiveActorList, name='GetCollectiveActorList'),

    # Regularity Panel
    path('GetRegularityAreaList/', views.GetRegularityAreaList, name='GetRegularityAreaList'),
    path('GetRegularityToolsList/', views.GetRegularityToolsList, name='GetRegularityToolsList'),
    path('GetRegularityLifeCycleList/', views.GetRegularityLifeCycleList, name='GetRegularityLifeCycleList'),
    path('GetRegulatorsByAreaId/<int:area_id>/', views.GetRegulatorsByAreaId, name='GetRegulatorsByAreaId'),
    path(
        'SearchDocumentsByRegulatorsKeywords/<int:country_id>/<str:tools_id>/<int:area_id>/<int:regulator_id>/<str:keywords_text>/',
        views.SearchDocumentsByRegulatorsKeywords, name='SearchDocumentsByRegulatorsKeywords'),
    path(
        'SearchDocumentsByRegulatorsLifeCycleAndKeywords/<int:country_id>/<str:tools_id>/<str:life_cycles>/<str:keywords_text>/',
        views.SearchDocumentsByRegulatorsLifeCycleAndKeywords, name='SearchDocumentsByRegulatorsLifeCycleAndKeywords'),
    path('RegularityLifeCycle/<int:country_id>/<str:tools_id>/<int:area_id>/<int:regulator_id>/<str:keywords_text>/',
         views.RegularityLifeCycle, name='RegularityLifeCycle'),
    path(
        'GetRegularityParagraphsDetails_Modal/<int:document_id>/<str:tools_id>/<int:area_id>/<int:regulator_id>/<str:keywords_text>/',
        views.GetRegularityParagraphsDetails_Modal, name='GetRegularityParagraphsDetails_Modal'),
    path('GetLifeCycleParagraphsDetails_Modal/<int:document_id>/<str:tools_id>/<str:life_cycles>/<str:keywords_text>/',
         views.GetLifeCycleParagraphsDetails_Modal, name='GetLifeCycleParagraphsDetails_Modal'),
    path('GetRegulatorsGraphData/<int:country_id>/<str:tools_id>/<int:area_id>/<int:regulator_id>/<str:keywords_text>/',
         views.GetRegulatorsGraphData, name='GetRegulatorsGraphData'),
    path(
        'GetRegulatorEdgeParagraphsByOperator_Modal/<int:country_id>/<int:tool_id>/<int:regulator_id>/<int:operator_id>/',
        views.GetRegulatorEdgeParagraphsByOperator_Modal, name='GetRegulatorEdgeParagraphsByOperator_Modal'),
    path(
        'GetRegulatorEdgeParagraphsByKeyword_Modal/<int:country_id>/<int:tool_id>/<int:area_id>/<int:regulator_id>/<str:keyword>/',
        views.GetRegulatorEdgeParagraphsByKeyword_Modal, name='GetRegulatorEdgeParagraphsByKeyword_Modal'),
    path(
        'GetRegularityParagraphsByToolName_Modal/<int:country_id>/<str:tool_name>/<int:area_id>/<int:regulator_id>/<str:keywords_text>/',
        views.GetRegularityParagraphsByToolName_Modal, name='GetRegularityParagraphsByToolName_Modal'),

    # Actors panel:
    path('GetActorCategoryList/', views.GetActorCategoryList, name='GetActorCategoryList'),
    path('GetActorsByCategoryId/<int:category_id>/', views.GetActorsByCategoryId, name='GetActorsByCategoryId'),
    path('GetActorRoleList/', views.GetActorRoleList, name='GetActorRoleList'),
    path('GetActorAreaList/', views.GetActorAreaList, name='GetActorAreaList'),

    path('GetSubAreasByAreaId/<int:area_id>/', views.GetSubAreasByAreaId, name='GetSubAreasByAreaId'),
    path('GetActorsByAreaID/<int:area_id>/', views.GetActorsByAreaID, name='GetActorsByAreaID'),

    # Actors tab
    path('GetActorParagraphsDetails_Modal/<int:country_id>/<int:actor_id>/<str:roles_id>/<str:keywords_text>/',
         views.GetActorParagraphsDetails_Modal, name='GetActorParagraphsDetails_Modal'),
    path(
        'GetActorParagraphsDetails_Modal_es/<int:country_id>/<int:actor_id>/<str:roles_id>/<str:keywords_text>/<int:curr_page>/',
        views.GetActorParagraphsDetails_Modal_es, name='GetActorParagraphsDetails_Modal_es'),
    path('SearchActorsByKeywords/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
         views.SearchActorsByKeywords, name='SearchActorsByKeywords'),
    path(
        'SearchActorsByKeywords_es/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/<int:curr_page>/',
        views.SearchActorsByKeywords_es, name='SearchActorsByKeywords_es'),
    path('GetActorParagraphsDetails_Modal/<int:country_id>/<int:actor_id>/<str:roles_id>/<str:keywords_text>/',
         views.GetActorParagraphsDetails_Modal, name='GetActorParagraphsDetails_Modal'),

    # Documents tab
    path(
        'SearchDocumentsByActorsKeywords/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
        views.SearchDocumentsByActorsKeywords, name='SearchDocumentsByActorsKeywords'),
    path(
        'SearchDocumentsByActorsKeywords_es/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/<int:curr_page>/',
        views.SearchDocumentsByActorsKeywords_es, name='SearchDocumentsByActorsKeywords_es'),
    path(
        'GetDocumentActorsDetails_Modal/<int:document_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
        views.GetDocumentActorsDetails_Modal, name='GetDocumentActorsDetails_Modal'),
    path(
        'GetDocumentActorsDetails_Modal_es/<int:document_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/<int:curr_page>/',
        views.GetDocumentActorsDetails_Modal_es, name='GetDocumentActorsDetails_Modal_es'),

    path('GetCorrelatedActors_ByActorID/<int:country_id>/<int:actor_id>/', views.GetCorrelatedActors_ByActorID,
         name='GetCorrelatedActors_ByActorID'),

    # Chart tab
    path('GetActorsDistChartData/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
         views.GetActorsDistChartData, name='GetActorsDistChartData'),
    path('GetActorsDistChartData_es/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
         views.GetActorsDistChartData_es, name='GetActorsDistChartData_es'),
    path(
        'GetColumnParagraphsByActorRoleName_Modal/<int:country_id>/<str:actor_name>/<str:role_name>/<str:keywords_text>/',
        views.GetColumnParagraphsByActorRoleName_Modal, name='GetColumnParagraphsByActorRoleName_Modal'),
    path(
        'GetColumnParagraphsByActorRoleName_Modal_es/<int:country_id>/<str:actor_name>/<str:role_name>/<str:keywords_text>/<int:curr_page>/',
        views.GetColumnParagraphsByActorRoleName_Modal_es, name='GetColumnParagraphsByActorRoleName_Modal_es'),
    path(
        'GetColumnParagraphsByActorRoleName_Modal_es_2/<str:actor_name>/<str:role_name>/<int:curr_page>/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.GetColumnParagraphsByActorRoleName_Modal_es_2, name='GetColumnParagraphsByActorRoleName_Modal_es_2'),
    path('GetParagraphsByIds_Modal/<str:keywords_text>/', views.GetParagraphsByIds_Modal,
         name='GetParagraphsByIds_Modal'),
    path('GetMaxMinEffectActorsInAreaChartData/<int:country_id>/<int:area_id>/<str:keywords_text>/',
         views.GetMaxMinEffectActorsInAreaChartData, name='GetMaxMinEffectActorsInAreaChartData'),
    path('GetMaxMinEffectActorsInAreaChartDataUsingCube/<int:country_id>/<int:area_id>/<int:sub_area_id>/',
         views.GetMaxMinEffectActorsInAreaChartDataUsingCube, name='GetMaxMinEffectActorsInAreaChartDataUsingCube'),
    path('getActorsWordCloudChartData/<int:country_id>/<int:area_id>/<int:actors_id>/',
         views.getActorsWordCloudChartData, name='getActorsWordCloudChartData'),

    # Actor-Keywords Graph tab
    path(
        'GetActorsKeywordsGraphData/<int:country_id>/<str:roles_id>/<int:category_id>/<str:actors_id>/<str:keywords_text>/',
        views.GetActorsKeywordsGraphData, name='GetActorsKeywordsGraphData'),
    path(
        'GetActorsKeywordsGraphData_es/<int:country_id>/<str:roles_id>/<int:category_id>/<str:actors_id>/<str:keywords_text>/',
        views.GetActorsKeywordsGraphData_es, name='GetActorsKeywordsGraphData_es'),
    path('GetActorsEdgeParagraphsByKeyword_Modal/<int:country_id>/<int:actor_id>/<str:roles_id>/<str:keyword>/',
         views.GetActorsEdgeParagraphsByKeyword_Modal, name='GetActorsEdgeParagraphsByKeyword_Modal'),
    path(
        'GetActorsEdgeParagraphsByKeyword_Modal_es/<int:country_id>/<int:actor_id>/<str:roles_id>/<str:keyword>/<int:curr_page>/',
        views.GetActorsEdgeParagraphsByKeyword_Modal_es, name='GetActorsEdgeParagraphsByKeyword_Modal_es'),

    # Actor-supervisors Graph tab
    path('GetActorsSupervisorsGraphData/<int:country_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
         views.GetActorsSupervisorsGraphData, name='GetActorsSupervisorsGraphData'),
    path('GetActorsSupervisorsGraphData_es/<int:country_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
         views.GetActorsSupervisorsGraphData_ES, name='GetActorsSupervisorsGraphData_ES'),
    path(
        'GetActorsSupervisorsEdge_Modal/<int:country_id>/<int:source_actor_id>/<int:supervisor_id>/<str:keywords_text>/',
        views.GetActorsSupervisorsEdge_Modal, name='GetActorsSupervisorsEdge_Modal'),
    path(
        'GetActorsSupervisorsEdge_Modal_es/<int:country_id>/<int:source_actor_id>/<int:supervisor_id>/<str:keywords_text>/<int:curr_page>/',
        views.GetActorsSupervisorsEdge_Modal_es, name='GetActorsSupervisorsEdge_Modal_es'),

    # Time-Series tab
    path('GetActorTimeSeries_ChartData_ByKeywords/<int:country_id>/<str:roles_id>/<int:actor_id>/<str:keywords_text>/',
         views.GetActorTimeSeries_ChartData_ByKeywords, name='GetActorTimeSeries_ChartData_ByKeywords'),
    path(
        'GetActorTimeSeries_ChartData_ByKeywords_es/<int:country_id>/<str:roles_id>/<int:actor_id>/<str:keywords_text>/',
        views.GetActorTimeSeries_ChartData_ByKeywords_es, name='GetActorTimeSeries_ChartData_ByKeywords_es'),
    path('GetActorTimeSeries_ChartData/<int:country_id>/<int:actor_id>/', views.GetActorTimeSeries_ChartData,
         name='GetActorTimeSeries_ChartData'),
    path('GetActorTimeSeries_Agile/<int:count_year>/<int:type>/<int:country_id>/<int:area_id>/',
         views.GetActorTimeSeries_Agile, name='GetActorTimeSeries_Agile'),
    path(
        'GetActorYearParagraphs_Line_Modal/<int:country_id>/<str:actor_name>/<str:actor_role_name>/<int:doc_year>/<str:keywords_text>/',
        views.GetActorYearParagraphs_Line_Modal, name='GetActorYearParagraphs_Line_Modal'),
    path(
        'GetActorYearParagraphs_Line_Modal_es/<int:country_id>/<str:actor_name>/<str:actor_role_name>/<int:doc_year>/<str:keywords_text>/<int:curr_page>/',
        views.GetActorYearParagraphs_Line_Modal_es, name='GetActorYearParagraphs_Line_Modal_es'),
    path('GetKeyWordActorParagraphs_Line_Modal/<int:country_id>/<str:actor_name>/<str:actor_role_name>/<int:doc_year>/',
         views.GetKeyWordActorParagraphs_Line_Modal, name='GetKeyWordActorParagraphs_Line_Modal'),

    path(
        'GetActorsComparison_ChartData/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
        views.GetActorsComparison_ChartData, name='GetActorsComparison_ChartData'),
    path(
        'GetActorsComparison_ChartData_es/<int:country_id>/<str:roles_id>/<int:area_id>/<str:actors_id>/<str:keywords_text>/',
        views.GetActorsComparison_ChartData_es, name='GetActorsComparison_ChartData_es'),
    path('getComparisonTrendChartsData_ByAtorsID/<int:country_id>/<int:source_actor_id>/<int:other_actor_id>/',
         views.getComparisonTrendChartsData_ByAtorsID, name='getComparisonTrendChartsData_ByAtorsID'),
    path('getComparisonSimilarityChartsData_ByActorsID/<int:country_id>/<int:source_actor_id>/<int:other_actor_id>/',
         views.getComparisonSimilarityChartsData_ByActorsID, name='getComparisonSimilarityChartsData_ByActorsID'),
    path('getComparisonAreaChartsData_ByActorsID/<int:country_id>/<int:source_actor_id>/<int:other_actor_id>/',
         views.getComparisonAreaChartsData_ByActorsID, name='getComparisonAreaChartsData_ByActorsID'),
    path('GetPredictionChartsData_ByAtorsID/<int:country_id>/<int:actor_id>/<str:model_name>/',
         views.GetPredictionChartsData_ByAtorsID, name='GetPredictionChartsData_ByAtorsID'),

    # Radar tab
    path('GetActorRolesRadar_ChartData/<int:country_id>/<str:roles_id>/<int:actor_id>/<str:keywords_text>/',
         views.GetActorRolesRadar_ChartData, name='GetActorRolesRadar_ChartData'),
    path('GetActorSubjectsRadar_ChartData/<int:country_id>/<str:roles_id>/<int:actor_id>/<str:keywords_text>/',
         views.GetActorSubjectsRadar_ChartData, name='GetActorSubjectsRadar_ChartData'),

    # Actor Graph panel
    path('GetActorGraphTypes/', views.GetActorGraphTypes, name='GetActorGraphTypes'),
    path(
        'Get_Actors_Correlation_GraphData/<int:country_id>/<int:graph_type_id>/<str:role_name>/<str:min_sim>/<str:max_sim>/',
        views.Get_Actors_Correlation_GraphData, name='Get_Actors_Correlation_GraphData'),

    # Official References panel
    path('searchDocumentsByOfficialReference/<int:country_id>/<str:subjects_id>/',
         views.searchDocumentsByOfficialReference, name='searchDocumentsByOfficialReference'),
    path('GetOfficialReferencesParagraphs_Detail_Modal/<int:document_id>/',
         views.GetOfficialReferencesParagraphs_Detail_Modal, name='GetOfficialReferencesParagraphs_Detail_Modal'),

    # Subject Statistics panel
    path('GetSubjectStatistics_ChartData/<int:country_id>/<str:document_tab_type>/',
         views.GetSubjectStatistics_ChartData, name='GetSubjectStatistics_ChartData'),
    path(
        'GetSubjectStatistics_Column_Modal/<int:country_id>/<str:document_tab_type>/<str:chart_type>/<str:column_name>/',
        views.GetSubjectStatistics_Column_Modal, name='GetSubjectStatistics_Column_Modal'),

    # adaptation (new)
    path(
        'SearchDocumentsByKeywords/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<str:place>/<str:keywords_text>/',
        views.SearchDocumentsByKeywords, name='SearchDocumentsByKeywords'),

    path('GetChartSloganAnalysis/<int:country_id>/<int:slogan_year>/', views.GetChartSloganAnalysis,
         name='GetChartSloganAnalysis'),
    path('GetInfoChartSloganAnalysis/<int:country_id>/<int:slogan_year>/', views.GetInfoChartSloganAnalysis,
         name='GetInfoChartSloganAnalysis'),
    path('GetDetailChartSloganAnalysis/<int:country_id>/<int:slogan_year>/<str:chart_type>/<str:column_name>/',
         views.GetDetailChartSloganAnalysis, name='GetDetailChartSloganAnalysis'),

    # Sample template
    path("sample_template/<str:panel_name>/", views.sample_template, name='sample_template'),
    path('searchDocumentsBy__keyword__/<str:panel_name>/<int:country_id>/<str:subjects>/',
         views.searchDocumentsBy__keyword__, name='searchDocumentsBy__keyword__'),
    path('Generate__keyword__ChartsData/<str:panel_name>/<int:country_id>/<str:subjects>/',
         views.Generate__keyword__ChartsData, name='Generate__keyword__ChartsData'),

    path('Get__keyword__Paragraphs_Detail_Modal/<int:document_id>/<str:keyword_list>/',
         views.Get__keyword__Paragraphs_Detail_Modal, name='Get__keyword__Paragraphs_Detail_Modal'),
    path(
        'GetPortalDocuments_ByColumn_Modal/<str:panel_name>/<int:country_id>/<str:subjects>/<str:chart_type>/<str:column_name>/',
        views.GetPortalDocuments_ByColumn_Modal, name='GetPortalDocuments_ByColumn_Modal'),
    path(
        'Get_Portal_ActorParagraphs_ByColumn_Modal/<str:panel_name>/<int:country_id>/<str:subjects_id>/<str:actor_name>/<str:role_name>/<str:keywords_text>/',
        views.Get_Portal_ActorParagraphs_ByColumn_Modal, name='Get_Portal_ActorParagraphs_ByColumn_Modal'),

    # -------------------------------------------

    path('GetAraByCountry_id/<int:country_id>/', views.GetAraByCountry_id, name='GetAraByCountry_id'),
    path('GetAraChartsData_ByCountryId/<int:country_id>/', views.GetAraChartsData_ByCountryId,
         name='GetAraChartsData_ByCountryId'),

    path('GetPrinciples/<int:country>/<str:text>/', views.GetPrinciples, name='GetPrinciples'),
    path('GetPrinciples/<int:country>/', views.GetPrinciples, name='GetAllPrinciples'),

    path('GetPrinciple_ChartsData/<int:country>/<str:text>/', views.GetPrinciple_ChartsData,
         name='GetPrinciple_ChartsData'),
    path('GetPrinciple_ChartsData/<int:country>/', views.GetPrinciple_ChartsData, name='GetPrinciple_ChartsData'),

    # business_advisor Panel
    path('SearchDocumentsByRegulators1/<int:country_id>/<int:area_id>/<int:regulator_id>/<str:person_id>/',
         views.SearchDocumentsByRegulators1, name='SearchDocumentsByRegulators'),
    path('Get__Paragraphs_Detail_Modal/<int:document_id>/', views.Get__Paragraphs_Detail_Modal,
         name='Get__Paragraphs_Detail_Modal'),
    path('make_chart_data_business_advisor/<int:country_id>/<int:area_id>/<int:regulator_id>/<str:person_id>/',
         views.make_chart_data_business_advisor, name='make_chart_data_business_advisor'),

    # AI
    path("AI_similarity_graph/", views.AI_similarity_graph, name='AI_similarity_graph'),
    path('AIGetGraphSimilarityMeasure/', views.AIGetGraphSimilarityMeasure,
         name='AIGetGraphSimilarityMeasure'),
    path('AI_predict_subject_LDA/<int:country_id>/<int:number_of_topic>/', views.GetDocumentsPredictSubjectLDA,
         name='GetDocumentsPredictSubjectLDA'),
    path("AIGetDocSimilarity/<int:country_id>/<int:measure_id>/", views.AIGetDocSimilarity, name='AIGetDocSimilarity'),
    path(
        'AIGetGraphEdgesByDocumentIdMeasure/<int:country_id>/<int:src_doc_id>/<int:src_type_id>/<int:src_subject_id>/<int:dest_doc_id>/<int:dest_type_id>/<int:dest_subject_id>/<int:measure_id>/<str:weight>/',
        views.AIGetGraphEdgesByDocumentIdMeasure, name='AIGetGraphEdgesByDocumentIdMeasure'),

    path("AI_topics/", views.AI_topics, name='AI_topics'),
    path("paragrraph_clustering/", views.paragrraph_clustering, name='paragrraph_clustering'),

    path("AIGetLDATopic/<int:country_id>/<int:number_of_topic>/<str:username>/", views.AIGetLDATopic,
         name='AIGetLDATopic'),
    path("AILDADocFromTopic/<int:topic_id>/", views.AILDADocFromTopic, name='AILDADocFromTopic'),
    path("AILDAWordCloudTopic/<int:topic_id>/", views.AILDAWordCloudTopic, name='AILDAWordCloudTopic'),
    path("AILDASubjectChartTopic/<int:topic_id>/", views.AILDASubjectChartTopic, name='AILDASubjectChartTopic'),

    path('GetLDAForDocByID/<int:document_id>/', views.GetLDAForDocByID, name='GetLDAForDocByID'),

    # collecive actor
    path(
        'SearchDocumentsByCollectiveActorsKeywords/<int:country_id>/<str:collectives_id>/<int:category_id>/<str:actors_id>/<str:membership_type>/<str:keywords_text>/<int:min_members_count>/',
        views.SearchDocumentsByCollectiveActorsKeywords, name='SearchDocumentsByCollectiveActorsKeywords'),
    path(
        'SearchDocumentsByCollectiveActorsKeywords_ES/<int:country_id>/<str:collectives_id>/<int:category_id>/<str:actors_id>/<str:membership_type>/<str:keywords_text>/<int:min_members_count>/<int:curr_page>/',
        views.SearchDocumentsByCollectiveActorsKeywords_ES,
        name='SearchDocumentsByCollectiveActorsKeywords_ESingest_rahbari_to_index'),
    path(
        'GetCollectiveActorsParagraphsDetails2/<int:document_id>/<str:collectives_id>/<int:category_id>/<str:actors_id>/<str:membership_type>/<str:keywords_text>/',
        views.GetCollectiveActorsParagraphsDetails2, name='GetCollectiveActorsParagraphsDetails2'),

    # executive
    path(
        'GetExecutiveRegulations/<int:country_id>/<int:area_id>/<str:multiselect_actor_value>/<int:type_id>/<int:from_year>/<int:to_year>/<int:curr_page>/',
        views.GetExecutiveRegulations, name='GetExecutiveRegulations'),
    path('GetExecutiveClauseParagraph/<int:clause_id>/', views.GetExecutiveClauseParagraph,
         name='GetExecutiveClauseParagraph'),
    path(
        'GetChartExecutiveRegulations/<int:country_id>/<int:area_id>/<str:multiselect_actor_value>/<int:type_id>/<int:from_year>/<int:to_year>/',
        views.GetChartExecutiveRegulations, name='GetChartExecutiveRegulations'),

    # compareDB
    path('GetOldNewDBCountries/<str:old_db_name>/<str:new_db_name>/', views.GetOldNewDBCountries,
         name='GetOldNewDBCountries'),
    path('GetCompareDocumentData/<int:src_country_id>/', views.GetCompareDocumentData,
         name='GetCompareDocumentData'),
    path('GetCompareDocumentListDetail/<int:src_country_id>/<str:type>/', views.GetCompareDocumentListDetail,
         name='GetCompareDocumentListDetail'),
    path('GetDocumentData/<int:src_country_id>/<int:dest_country_id>/<str:type>/', views.GetDocumentData,
         name='GetDocumentData'),
    path('GetDocumentByListId/<str:db_name>/', views.GetDocumentByListId, name='GetDocumentByListId'),

    path('ShowMyUserProfile/', views.ShowMyUserProfile, name='ShowMyUserProfile'),
    path('GetMyUserProfile/', views.GetMyUserProfile, name='GetMyUserProfile'),
    path('SetMyUserProfile/', views.SetMyUserProfile, name='SetMyUserProfile'),
    path('ChangePassword/<str:old_password>/<str:new_password>/', views.ChangePassword, name='ChangePassword'),
    path('ShowUserProfile/', views.ShowUserProfile, name='ShowUserProfile'),
    path('GetUserProfile/<int:id>/', views.GetUserProfile, name='GetUserProfile'),

    path('get_pending_followers/', views.get_pending_followers, name='get_pending_followers'),
    path('accept_follower/<int:id>/', views.accept_follower, name='accept_follower'),
    path('reject_follower/<int:id>/', views.reject_follower, name='reject_follower'),

    # book
    path('submit_book_api/', views.submit_book_api, name='submit_book_api'),
    path('download_book/<str:folder_name>/<str:filename>/', views.download_book, name='download_book'),

    path('create_expertise_sample/', views.create_expertise_sample, name='create_expertise_sample'),
    path('get_excels_data_book/<int:country_id>/', views.get_excels_data_book, name='get_excels_data_book'),

    path('GetUnknownDocuments/', views.GetUnknownDocuments, name='GetUnknownDocuments'),

    path('get_similarity_highlighted_text/<int:doc_id_1>/<int:doc_id_2>/<str:measure>/',
         views.get_similarity_highlighted_text, name='get_similarity_highlighted_text'),
    path('cancellation/', views.cancellation, name='cancellation'),
    path('indictment_to_db/<int:id>/', views.indictment_to_db, name='indictment_to_db'),
    path('GetIndictmentDocs/', views.GetIndictmentDocs, name='GetIndictmentDocs'),

    path('ingest_documents_to_index/<int:id>/<str:language>/', views.ingest_documents_to_index,
         name='ingest_documents_to_index'),
    path('ingest_document_actor_to_index/<int:id>/<str:language>/', views.ingest_document_actor_to_index,
         name='ingest_document_actor_to_index'),
    path('ingest_actor_supervisor_to_index/<int:id>/<str:language>/', views.ingest_actor_supervisor_to_index,
         name='ingest_actor_supervisor_to_index'),
    path('ingest_spatiotemporal_to_index/<int:id>/', views.ingest_spatiotemporal_to_index,
         name='ingest_spatiotemporal_to_index'),

    path('ingest_judgments_to_index/<int:id>/<str:language>/', views.ingest_judgments_to_index,
         name='ingest_judgments_to_index'),
    path('ingest_revoked_documents/<int:id>/<str:language>/', views.ingest_revoked_documents,
         name='ingest_revoked_documents'),
    path('ingest_paragraphs_to_index/<int:id>/<str:language>/<int:is_for_ref>/', views.ingest_paragraphs_to_index,
         name='ingest_paragraphs_to_index'),
    path('ingest_standard_documents_to_index/<int:id>/<str:language>/', views.ingest_standard_documents_to_index,
         name='ingest_standard_documents_to_index'),
    path('ingest_terminology_to_index/<int:id>/<str:language>/', views.ingest_terminology_to_index,
         name='ingest_terminology_to_index'),
    path('ingest_full_profile_analysis_to_elastic/<int:id>/', views.ingest_full_profile_analysis_to_elastic,
         name='ingest_full_profile_analysis_to_elastic'),
    path('executive_clauses_extractor/<int:id>/', views.executive_clauses_extractor,
         name='executive_clauses_extractor'),
    path('clause_extractor/<int:id>/', views.clause_extractor,
         name='clause_extractor'),
    path('ingest_rahbari_to_index/<int:id>/', views.ingest_rahbari_to_index,
         name='ingest_rahbari_to_index'),

    path('ingest_rahbari_to_sim_index/<int:id>/', views.ingest_rahbari_to_sim_index,
         name='ingest_rahbari_to_sim_index'),

    path('ingest_document_collective_members_to_index/<int:id>/', views.ingest_document_collective_members_to_index,
         name='ingest_document_collective_members_to_index'),

    path('ingest_clustering_paragraphs_to_index/<int:id>/<str:language>/', views.ingest_clustering_paragraphs_to_index,
         name='ingest_clustering_paragraphs_to_index'),

    path('ingest_books/<int:id>/', views.ingest_books,
         name='ingest_books'),


    path('GetSearchDetails_ES_Rahbari/<int:document_id>/<str:search_type>/<str:text>/',
         views.GetSearchDetails_ES_Rahbari, name='GetSearchDetails_ES_Rahbari'),

    path('GetSearchDetails_ES_Rahbari_2/<int:document_id>/<str:search_type>/<str:text>/<int:isRule>/',
         views.GetSearchDetails_ES_Rahbari_2, name='GetSearchDetails_ES_Rahbari_2'),

    path('GetRahbariTypeDetails_ES/<int:document_id>/<int:rahbari_type_id>/',
         views.GetRahbariTypeDetails_ES, name='GetRahbariTypeDetails_ES'),

    path(
        'rahbari_get_full_profile_analysis/<int:country_id>/<int:type_id>/<str:label_name>/<int:from_year>/<int:to_year>/<str:rahbari_type>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.rahbari_get_full_profile_analysis, name='rahbari_get_full_profile_analysis'),

    path('rahbari_similarity_calculation/<int:id>/', views.rahbari_similarity_calculation,
         name='rahbari_similarity_calculation'),

    path('ingest_standard_documents_to_sim_index/<int:id>/<str:language>/',
         views.ingest_standard_documents_to_sim_index, name='ingest_standard_documents_to_sim_index'),
    path('books_similarity_calculation/<int:id>/', views.books_similarity_calculation,
         name='books_similarity_calculation'),
    path('books_similarity_calculation_cube/<int:id>/', views.books_similarity_calculation_cube,
         name='books_similarity_calculation_cube'),
    path('paragraphs_similarity_calculation/<int:id>/', views.paragraphs_similarity_calculation,
         name='paragraphs_similarity_calculation'),
    path('rahbari_paragraphs_similarity_calculation/<int:id>/', views.rahbari_paragraphs_similarity_calculation,
         name='rahbari_paragraphs_similarity_calculation'),

    path('GetSimiGraphEdgesByDocumentsList_Standard/<str:measure_name>/',
         views.GetSimiGraphEdgesByDocumentsList_Standard, name='GetSimiGraphEdgesByDocumentsList_Standard'),

    path('update_file_name_extention/<int:id>/', views.update_file_name_extention, name='update_file_name_extention'),

    path('update_judgment_name/<int:id>/', views.update_judgment_name, name='update_judgment_name'),

    path('ARIMA_Prediction_TO_DB/<int:id>/', views.ARIMA_Prediction_TO_DB, name='ARIMA_Prediction_TO_DB'),

    path('revoked_types_to_db/<int:id>/', views.revoked_types_to_db, name='revoked_types_to_db'),
    path('subject_area_keywords_to_db/<int:id>/', views.subject_area_keywords_to_db,
         name='subject_area_keywords_to_db'),

    path('rahbari_update_fields_from_file/<int:id>/', views.rahbari_update_fields_from_file,
         name='rahbari_update_fields_from_file'),


    path('clustering_algorithms_to_db/<int:id>/', views.clustering_algorithms_to_db,
         name='clustering_algorithms_to_db'),

    path('rahbari_labels_to_db/<int:id>/', views.rahbari_labels_to_db,
         name='rahbari_labels_to_db'),

    path('seen_help/<str:url>/', views.seen_help, name='seen_help'),
    path('saw_help/<str:url>/', views.saw_help, name='saw_help'),

    path('GetRevokedTableData/<int:country_id>/', views.GetRevokedTableData, name='GetRevokedTableData'),

    path('GetDetailRevokedData/<int:src_para_id>/<int:dest_para_id>/<int:dest_document_id>/',
         views.GetDetailRevokedData, name='GetDetailRevokedData'),
    path('GetDetailRevokedData_2/<int:src_para_id>/<int:dest_para_id>/<int:src_id>/<int:dest_id>/',
         views.GetDetailRevokedData_2, name='GetDetailRevokedData_2'),
    path('RevokedSearch_ES/<int:country_id>/<str:RevokedType_text>/<str:RevokedSize_text>/<str:SubType_text>/<str:place>/<str:text>/',
        views.RevokedSearch_ES, name='RevokedSearch_ES'),
    path('RevokedSearch_ES2/<int:country_id>/<str:RevokedType_text>/<str:RevokedSize_text>/<str:SubType_text>/<str:place>/<str:text>/<int:curr_page>/',
        views.RevokedSearch_ES2, name='RevokedSearch_ES2'),

    path('remove_unknown_standard_doc/<int:country_id>/', views.remove_unknown_standard_doc,
         name='remove_unknown_standard_doc'),

    path('GetDoticSimDocument/<int:document_id>/', views.GetDoticSimDocument, name='GetDoticSimDocument'),
    path('GetDoticSimDocument_ByTitle/<str:document_name>/', views.GetDoticSimDocument_ByTitle, name='GetDoticSimDocument_ByTitle'),
    path('GetDoticSimDocument_ByLabels/<int:document_id>/', views.GetDoticSimDocument_ByLabels, name='GetDoticSimDocument_ByLabels'),
    path('GetDetail_DoticSimDocument_ByLabels/<int:src_document_id>/<int:dest_document_id>/', views.GetDetail_DoticSimDocument_ByLabels, name='GetDetail_DoticSimDocument_ByLabels'),
    


    path('GetParaSimilarity/<int:doc1_id>/<int:doc2_id>/', views.GetParaSimilarity, name='GetParaSimilarity'),

    path("document_subject_area/", views.document_subject_area, name='document_subject_area'),

    path(
        'Get_SubjectArea_Documents/<int:country_id>/<int:SubjectAreaSelect_id>/<str:multiselect_SubjectSubArea_value>/<str:ValidationSelect>/<str:RevokedSizeSelect>/<str:SubTypeSelect>/',
        views.Get_SubjectArea_Documents, name='Get_SubjectArea_Documents'),

    path("GetSubjectAreaGraphNodesEdges/<int:country_id>/<int:area_id>/", views.GetSubjectAreaGraphNodesEdges,
         name='GetSubjectAreaGraphNodesEdges'),
    path("GetSubjectSubAreaList/<int:area_id>/", views.GetSubjectSubAreaList, name='GetSubjectSubAreaList'),

    path('documentSubjecArea_ES/<int:country_id>/<int:SubjectAreaSelect_id>/<str:multiselect_SubjectSubArea_value>/',
         views.documentSubjecArea_ES, name='documentSubjecArea_ES'),
    path("GetDocumentWithAreaKeywords/<int:document_id>/", views.GetDocumentWithAreaKeywords,
         name='GetDocumentWithAreaKeywords'),

    path('GetParagraphWithAreaKeywords/<int:document_id>/', views.GetParagraphWithAreaKeywords,
         name='GetParagraphWithAreaKeywords'),

    path('trial_law_import/<int:id>/', views.trial_law_import, name='trial_law_import'),
    path('GetTrialLawByCountryId/<int:country_id>/<str:host>/', views.GetTrialLawByCountryId,
         name='GetTrialLawByCountryId'),

    path("SubjectKeywordGraph/", views.SubjectKeywordGraph, name='SubjectKeywordGraph'),
    path("SubjectKeywordGraphExtractor/<int:version>/", views.SubjectKeywordGraphExtractor,
         name='SubjectKeywordGraphExtractor'),
    path("TextSubjectExtractor/", views.TextSubjectExtractor, name='TextSubjectExtractor'),
    path("GetSubjectListByVersionId/<int:version>/", views.GetSubjectListByVersionId, name='GetSubjectListByVersionId'),

    path("ManualClustering/", views.ManualClustering, name='ManualClustering'),
    path("BoostingSearchParagraph_ES/<int:country_id>/<int:curr_page>/<int:result_size>/",
         views.BoostingSearchParagraph_ES, name='BoostingSearchParagraph_ES'),

    path("BoostingSearchKnowledgeGraph_ES/<int:country_id>/<str:field_name>/<str:field_value>/<str:language>/<str:search_type>/<int:curr_page>/<int:result_size>/",
        views.BoostingSearchKnowledgeGraph_ES, name='BoostingSearchKnowledgeGraph_ES'),


    path(
        "BoostingSearchParagraph_Column_ES/<int:country_id>/<str:field_name>/<str:field_value>/<int:curr_page>/<int:result_size>/",
        views.BoostingSearchParagraph_Column_ES, name='BoostingSearchParagraph_Column_ES'),

    # ----------- LDA heatmap -----------------
    path("AIGet_Topic_Centers_CahrtData/<int:country_id>/<int:number_of_topic>/", views.AIGet_Topic_Centers_CahrtData,
         name='AIGet_Topic_Centers_CahrtData'),
    path('GetLDAGraphData/<int:country_id>/<int:number_of_topic>/', views.GetLDAGraphData,
         name='GetLDAGraphData'),

    path('GetLDAKeywordGraphData/<int:country_id>/<int:number_of_topic>/', views.GetLDAKeywordGraphData,
         name='GetLDAKeywordGraphData'),

    path('save_lda_topic_label/<str:topic_id>/<str:username>/<str:label>/', views.save_lda_topic_label,
         name='save_lda_topic_label'),

    # -------------- Clustering ----------------
    path(
        'GetParagraph_Clusters/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/<str:username>/',
        views.GetParagraph_Clusters, name='GetParagraph_Clusters'),
    path(
        'Get_ClusterCenters_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/',
        views.Get_ClusterCenters_ChartData, name='Get_ClusterCenters_ChartData'),
    path(
        'Get_ClusteringAlgorithm_DiscriminatWords_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/',
        views.Get_ClusteringAlgorithm_DiscriminatWords_ChartData,
        name='Get_ClusteringAlgorithm_DiscriminatWords_ChartData'),

    path('Get_Clustering_Vocabulary/<int:country_id>/<str:vector_type>/<str:ngram_type>/',
         views.Get_Clustering_Vocabulary,
         name='Get_Clustering_Vocabulary'),

    path(
        'Get_ClusteringEvaluation_Silhouette_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<str:ngram_type>/',
        views.Get_ClusteringEvaluation_Silhouette_ChartData, name='Get_ClusteringEvaluation_Silhouette_ChartData'),
    path('save_topic_label/<str:topic_id>/<str:username>/<str:label>/', views.save_topic_label,
         name='save_topic_label'),

    path('Get_Topic_Paragraphs/<int:country_id>/<str:topic_id>/', views.Get_Topic_Paragraphs,
         name='Get_Topic_Paragraphs'),
    path(
        'Get_Topic_Paragraphs_ES/<int:country_id>/<str:topic_id>/<int:result_size>/<int:curr_page>/<int:get_paragraphs>/<int:get_aggregations>/',
        views.Get_Topic_Paragraphs_ES, name='Get_Topic_Paragraphs_ES'),
    path(
        'Get_Topic_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:field_name>/<str:field_value>/<int:curr_page>/<int:result_size>/',
        views.Get_Topic_Paragraphs_Column_ES, name='Get_Topic_Paragraphs_Column_ES'),
    path(
        'Get_ANOVA_Word_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:word>/<int:curr_page>/<int:result_size>/',
        views.Get_ANOVA_Word_Paragraphs_Column_ES, name='Get_ANOVA_Word_Paragraphs_Column_ES'),
    path(
        'Export_ANOVA_Word_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:word>/<str:username>/<int:curr_page>/<int:result_size>/',
        views.Export_ANOVA_Word_Paragraphs_Column_ES, name='Export_ANOVA_Word_Paragraphs_Column_ES'),

    path('Excel_Topic_Paragraphs_ES/<int:country_id>/<str:topic_id>/<int:result_size>/<int:curr_page>/<str:username>/',
         views.Excel_Topic_Paragraphs_ES, name='Excel_Topic_Paragraphs_ES'),

    path('Get_Topic_Anova_ChartData/<int:country_id>/<str:topic_id>/', views.Get_Topic_Anova_ChartData,
         name='Get_Topic_Anova_ChartData'),
    path('Get_Topic_TagCloud_ChartData/<int:country_id>/<str:topic_id>/', views.Get_Topic_TagCloud_ChartData,
         name='Get_Topic_TagCloud_ChartData'),

    path('delete_topic_paragraphs/', views.delete_topic_paragraphs, name='delete_topic_paragraphs'),

    path(
        'GetClusteringGraphData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:ngram_type>/',
        views.GetClusteringGraphData,
        name='GetClusteringGraphData'),

    path(
        'GetClusterKeywordGraphData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:ngram_type>/',
        views.GetClusterKeywordGraphData,
        name='GetClusterKeywordGraphData'),

    path(
        'GetKeywordClustersData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:keyword>/',
        views.GetKeywordClustersData,
        name='GetKeywordClustersData'),

    path('GetKeywordLDAData/<int:country_id>/<int:cluster_size>/<str:username>/<str:keyword>/', views.GetKeywordLDAData,
         name='GetKeywordLDAData'),

    path('insert_subject_keyword_list/<int:id>/', views.insert_subject_keyword_list,
         name='insert_subject_keyword_list'),
    path('GetSubjectKeywordGraphVersion/', views.GetSubjectKeywordGraphVersion, name='GetSubjectKeywordGraphVersion'),

    path('GetSubjectKeywordsListBySubjectId/<int:subject_id>/', views.GetSubjectKeywordsListBySubjectId,
         name='GetSubjectKeywordsListBySubjectId'),
    path('GetSubjectDocumentChartDataBySubjectId/<int:subject_id>/', views.GetSubjectDocumentChartDataBySubjectId,
         name='GetSubjectDocumentChartDataBySubjectId'),
    path('GetSubjectDocumentParagraphListBySubjectId/<int:subject_id>/<str:host>/',
         views.GetSubjectDocumentParagraphListBySubjectId, name='GetSubjectDocumentParagraphListBySubjectId'),
    path('CreateDocumentCSVDataBySubjectId/<int:subject_id>/', views.CreateDocumentCSVDataBySubjectId,
         name='CreateDocumentCSVDataBySubjectId'),

    path('DeleteCreatedCSVFile/<str:file_name>/', views.DeleteCreatedCSVFile, name='DeleteCreatedCSVFile'),
    path('delete_lda_table/', views.delete_lda_table, name='delete_lda_table'),

    path('knowledgeGraph/', views.knowledgeGraph, name='knowledgeGraph'),

    path('SaveKnowledgeGraph/<str:graph_name>/<str:username>/<int:graph_id>/', views.SaveKnowledgeGraph,
         name='SaveKnowledgeGraph'),
    path('DeleteKnowledgeGraph/<int:graph_id>/', views.DeleteKnowledgeGraph, name='DeleteKnowledgeGraph'),

    path('sentiment_analysis/', views.sentiment_analysis_panel, name='sentimentAnalysis'),
    path('tagAnalyser/<str:text>/', views.tagging_analyser, name='tag_analysis'),
    path('sentimentAnalyser/<str:text>/', views.sentiment_analyser, name='sentiment_analysis'),
    path('classificationAnalyser/<str:text>/', views.classification_analyser,
         name='classification_analysis'),

    path('auto_translator/<str:text>/', views.auto_translator,
         name='auto_translator'),



    path('GetParagraphBy_ID/<int:paragraph_id>/', views.GetParagraphBy_ID,
         name='GetParagraphBy_ID'),

    path('GetParagraphSubjectContent/<int:paragraph_id>/<int:version_id>/', views.GetParagraphSubjectContent,
         name='GetParagraphSubjectContent'),

    path('GetAllKnowledgeGraphList/<str:username>/', views.GetAllKnowledgeGraphList,
         name='GetAllKnowledgeGraphList'),

    path('GetKnowledgeGraphData/<int:version_id>/', views.GetKnowledgeGraphData,
         name='GetKnowledgeGraphData'),

    path('findActor/<int:id>/', views.findActor,
         name='findActor'),

    path('fullProfileAnalysis/<int:id>/', views.fullProfileAnalysis, name='fullProfileAnalysis'),

    path('delete_nadarad_document/', views.delete_nadarad_document,
         name='delete_nadarad_document'),

    path('GetSubjectsListByKeywordId/<int:version_id>/<str:keyword_name>/', views.GetSubjectsListByKeywordId,
         name='GetSubjectsListByKeywordId'),

    path('GetTextSummary/', views.GetTextSummary,
         name='GetTextSummary'),

     #/****** Rahbari Labels ******/
    path('GetLabelTimeSeries_ChartData/<str:label_name>/', views.GetLabelTimeSeries_ChartData, name='GetLabelTimeSeries_ChartData'),
    path('GetAffinityLabels_ByLabelName/<str:label_name>/', views.GetAffinityLabels_ByLabelName, name='GetAffinityLabels_ByLabelName'),

    path('GetCorrelatedLabels_ByLabelName/<str:label_name>/', views.GetCorrelatedLabels_ByLabelName, name='GetCorrelatedLabels_ByLabelName'),
    path('GetCorrelatedLabels_TimeSeries_ChartData/<str:source_label_name>/<str:dest_label_name>/', views.GetCorrelatedLabels_TimeSeries_ChartData, name='GetCorrelatedLabels_TimeSeries_ChartData'),



    #/****** Advanced ARIMA ******/

    path('GetActorTimeSeries_ChartDataAdvance/<int:country_id>/<int:actor_id>/', views.GetActorTimeSeries_ChartDataAdvance, name='GetActorTimeSeries_ChartDataAdvance'),
    path('ARIMA_Prediction_TO_DB_2/<int:id>/', views.ARIMA_Prediction_TO_DB_2, name='ARIMA_Prediction_TO_DB_2'),

    #/****** AnalysisKnowledgeGraph ******/
    path('DocAnalysisKnowledgeGraph/<int:id>/', views.DocAnalysisKnowledgeGraph, name='DocAnalysisKnowledgeGraph'),

    path('DocAnalysisKnowledgeGraphPOS/<int:id>/', views.DocAnalysisKnowledgeGraphPOS, name='DocAnalysisKnowledgeGraphPOS'),

    path('RahabriCoLabelsGraph/<int:id>/', views.RahabriCoLabelsGraph, name='RahabriCoLabelsGraph'),
    path('RahbariGraphUpload/<int:id>/', views.RahbariGraphUpload, name='RahbariGraphUpload'),
    path('RahbariTypeExtractor/<int:id>/', views.RahbariTypeExtractor, name='RahbariTypeExtractor'),
    path('rahbari_correlated_labels_extractor/<int:id>/', views.rahbari_correlated_labels_extractor, name='rahbari_correlated_labels_extractor'),
    path('insert_docs_to_rahbari_table/<int:id>/', views.insert_docs_to_rahbari_table, name='insert_docs_to_rahbari_table'),



    path("rahbari_graph/", views.rahbari_graph, name='rahbari_graph'),
    path('getRahbariCoLabelsGraphMinMaxWeight/', views.getRahbariCoLabelsGraphMinMaxWeight, name='getRahbariCoLabelsGraphMinMaxWeight'),
    path('getRahbariGraphData/<int:type_id>/<int:limit_neighbour_count>/<str:keyword>/<int:level>/', views.getRahbariGraphData, name='getRahbariGraphData'),
    path("getRahbariGraphType/", views.getRahbariGraphType, name='getRahbariGraphType'),


    path("GetRahbariTypes/", views.GetRahbariTypes, name='GetRahbariTypes'),
    path("GetRahbariLabels/", views.GetRahbariLabels, name='GetRahbariLabels'),
    path('GetRahbariTypeDetail/<int:document_id>/', views.GetRahbariTypeDetail, name='getRahbariGraphData'),

    path("delete_user/", views.delete_user, name='delete_user'),
]
