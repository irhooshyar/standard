from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.UserRole)
admin.site.register(models.User)
admin.site.register(models.UserLogs)

admin.site.register(models.Country)
admin.site.register(models.Level)
admin.site.register(models.RegularityTools)
admin.site.register(models.CollectiveActor)
admin.site.register(models.DeployServer)
admin.site.register(models.RegularityArea)
admin.site.register(models.Regulator)
admin.site.register(models.KeywordList)
admin.site.register(models.Type)
admin.site.register(models.ApprovalReference)
admin.site.register(models.Subject)
admin.site.register(models.SubjectKeyWords)
admin.site.register(models.LegalOrientation)
admin.site.register(models.LegalOrientationKeyWords)
admin.site.register(models.ActorCategory)
admin.site.register(models.ActorType)
admin.site.register(models.Document)
admin.site.register(models.Measure)
admin.site.register(models.Slogan)
admin.site.register(models.SloganAnalysis)
admin.site.register(models.DocumentSubject)
admin.site.register(models.DocumentLegalOrientation)
admin.site.register(models.DocumentWords)
admin.site.register(models.DocumentTFIDF)
admin.site.register(models.DocumentSubjectKeywords)
admin.site.register(models.DocumentKeywords)
admin.site.register(models.DocumentParagraphs)
admin.site.register(models.DocumentGeneralDefinition)
admin.site.register(models.Actor)
admin.site.register(models.Operator)
admin.site.register(models.DocumentActor)
admin.site.register(models.DocumentClause)
admin.site.register(models.ActorSupervisor)
admin.site.register(models.DocumentRegulator)
admin.site.register(models.RegulatorOperator)
admin.site.register(models.DocumentNgram)
admin.site.register(models.DocumentDefinition)
admin.site.register(models.ExtractedKeywords)
admin.site.register(models.ReferencesParagraphs)
admin.site.register(models.Graph)



admin.site.register(models.ExecutiveRegulations)




# added



# Actor














# CUBEs
admin.site.register(models.CUBE_DocumentJsonList)

admin.site.register(models.CUBE_SubjectStatistics_FullData)
admin.site.register(models.CUBE_SubjectStatistics_ChartData)

admin.site.register(models.CUBE_Template_FullData)
admin.site.register(models.CUBE_Template_ChartData)
admin.site.register(models.CUBE_Template_TableData)

admin.site.register(models.CUBE_Subject_TableData)

admin.site.register(models.CUBE_CollectiveActor_TableData)
admin.site.register(models.CUBE_RegularityLifeCycle_TableData)

admin.site.register(models.CUBE_Votes_FullData)
admin.site.register(models.CUBE_Votes_ChartData)
admin.site.register(models.CUBE_Votes_TableData)

admin.site.register(models.Template_Panels_Info)






# admin.site.register(models.Principle)
admin.site.register(models.CUBE_Principles_TableData)
admin.site.register(models.CUBE_Principles_FullData)
admin.site.register(models.CUBE_Principles_ChartData)



admin.site.register(models.CUBE_MandatoryRegulations_TableData)
admin.site.register(models.CUBE_MaxMinEffectActorsInArea_ChartData)