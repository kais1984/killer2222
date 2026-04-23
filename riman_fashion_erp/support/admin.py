from django.contrib import admin
from .models import *

# Simple registration of all support models
admin.site.register(SupportTicket)
admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
admin.site.register(KnowledgeBase)
admin.site.register(FAQ)
admin.site.register(Warranty)
admin.site.register(WarrantyClaim)
admin.site.register(SurveyTemplate)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyResponse)
admin.site.register(SurveyAnswer)
