from json import tool
from django.db import models
from django.db.models.base import Model


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    file = models.FileField(null=True, blank=True, upload_to='upload')

    file_name = models.CharField(null=True, max_length=500)
    language = models.CharField(null=True, max_length=500)
    status = models.CharField(null=True, blank=True, max_length=1000, default="Done")

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Language: {self.language}'


class BookCountry(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    file = models.FileField(null=True, blank=True, upload_to='upload')

    file_name = models.CharField(null=True, max_length=500)
    language = models.CharField(null=True, max_length=500)
    status = models.CharField(null=True, blank=True, max_length=1000, default="Done")

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Language: {self.language}'

class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'


class ApprovalReference(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'

class Actor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    parent_id = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'

class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=1000)
    color = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Color: {self.color}'


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=3000)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    level_id = models.ForeignKey(Level, null=True, on_delete=models.CASCADE)
    level_name = models.CharField(null=True, max_length=500)

    type_id = models.ForeignKey(Type, null=True, on_delete=models.CASCADE)
    type_name = models.CharField(null=True, max_length=500)

    approval_reference_id = models.ForeignKey(ApprovalReference, null=True, on_delete=models.CASCADE)
    approval_reference_name = models.CharField(null=True, max_length=500)

    approval_date = models.CharField(null=True, max_length=500)
    communicated_date = models.CharField(null=True, max_length=500)

    word_count = models.IntegerField(null=True)
    distinct_word_count = models.IntegerField(null=True)
    stopword_count = models.IntegerField(null=True)

    json_text = models.JSONField(null=True)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Country_ID: {self.country_id}'


class Measure(models.Model):
    id = models.AutoField(primary_key=True)
    persian_name = models.CharField(null=True, max_length=500)
    english_name = models.CharField(null=True, max_length=500)
    type = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.persian_name}'

class DocumentWords(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=500)
    count = models.FloatField(default=0)
    gram = models.FloatField(null=True)
    place = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Word: {self.word}, Count: {self.count}, place: {self.place},'


class DocumentTFIDF(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=500)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Word: {self.word}, Count: {self.count}, Weight: {self.weight}'


class DocumentParagraphs(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, max_length=1000)
    number = models.IntegerField(default=0)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Number: {self.number}'


class DocumentActor(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(Actor, null=True, on_delete=models.CASCADE)
    paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Actor_ID: {self.actor_id}, Paragraph_ID: {self.paragraph_id}'


class DocumentNgram(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.CharField(null=True, max_length=500)
    gram = models.IntegerField(default=1)
    count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Text: {self.text}, Gram: {self.gram}, Count: {self.count}'


class DocumentDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, max_length=1000)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}'


class DocumentGeneralDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    keyword = models.CharField(null=True, max_length=100)
    text = models.TextField(null=True, max_length=5000)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}'


class ExtractedKeywords(models.Model):
    id = models.AutoField(primary_key=True)
    definition_id = models.ForeignKey(DocumentDefinition, null=True, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=1000)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Definition_Id: {self.definition_id}, Name: {self.word}'


class ReferencesParagraphs(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Document_References_Id: {self.document_id}, Document_Paragraphs_Id: {self.paragraph_id}'


class Graph(models.Model):
    id = models.AutoField(primary_key=True)
    src_document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='src_doc_id')
    dest_document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='dest_doc_id')
    measure_id = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Src_Document_ID: {self.src_document_id}, Dest_Document_ID: {self.dest_document_id}, Measure_ID: {self.measure_id}, Weight: {self.weight}'


class CUBE_DocumentJsonList(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    json_text = models.JSONField(null=True)

    class Meta:
        app_label = 'en_doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country_id} , Json_Text: {self.json_text}'


# -------------- AI Analysis ------------------------------------
class AINamedEntities(models.Model):
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    entities = models.JSONField(null=True)

    class Meta:
        app_label = 'en_doc'

