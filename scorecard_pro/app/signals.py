# from django.db.models.signals import post_save,post_delete
# # from . import models
# from django.dispatch import receiver
# from app import models as app_models


# # @receiver(post_save,sender=app_models.ProductivityMetrics)
# # def post_save_metrices(sender,instance,created,**kwargs):
# #     if created:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,productivity_metrics=instance.productivity_metrics).save()
# #         else:
# #             data = data[0](productivity_metrics=instance.productivity_metrics)
# #             data.save()
# #     else:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,productivity_metrics=instance.productivity_metrics).save()
# #         else:
# #             data = data[0](productivity_metrics=instance.productivity_metrics)
# #             data.save()
# #         # print('instance productivity_metrics ===updated',instance.employee_id)


# # @receiver(post_save,sender=app_models.QualityMetrics)
# # def post_save_metrices(sender,instance,created,**kwargs):
# #     if created:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,quality_metrics=instance.quality_score).save()
# #         else:
# #             del data[0]['quality_metrics']
# #             data = data[0](quality_metrics=instance.quality_score,**data[0])
# #             data.save()
# #     else:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,quality_metrics=instance.quality_score).save()
# #         else:
# #             data = data[0](quality_metrics=instance.quality_score)
# #             data.save()
# #         # print('instance productivity_metrics ===updated',instance.employee_id)


# # @receiver(post_save,sender=app_models.TimelinessMetrics)
# # def post_save_metrices(sender,instance,created,**kwargs):
# #     if created:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,timeliness_metrics=instance.timeliness_score).save()
# #         else:
# #             data = data[0](timeliness_metrics=instance.timeliness_score)
# #             data.save()
# #         # app_models.Metrics(employee_id=instance.employee_id,timeliness_metrics=instance.timeliness_score).save()
# #     else:
# #         data = app_models.Metrics.objects.filter(employee_id=instance.employee_id).values()
# #         if not data:
# #             app_models.Metrics(employee_id=instance.employee_id,timeliness_metrics=instance.timeliness_score).save()
# #         else:
# #             data = data[0](timeliness_metrics=instance.timeliness_score)
# #             data.save()
# #         # app_models.Metrics(employee_id=instance.employee_id,timeliness_metrics=instance.timeliness_score).save()
# #         # print('instance productivity_metrics ===updated',instance.employee_id)


# @receiver(post_save,sender=app_models.Metrics)
# def post_save_metrices(sender,instance,created,**kwargs):
#     if created:
#         p=app_models.ProductivityMetrics.objects.get(employee_id=instance.employee_id).productivity_metrics
#         q=app_models.QualityMetrics.objects.get(employee_id=instance.employee_id).quality_score
#         t=app_models.TimelinessMetrics.objects.get(employee_id=instance.employee_id).timeliness_score
#         data = app_models.Weights.objects.all()[0]
#         if p and q and t:
#             score = ((p * data.productivity_per_cent)/100)+((q*data.quality_per_cent)/100)+((t*data.timeliness_per_cent)/100)
#             app_models.ScoreTable(employee_id=instance.employee_id,score=score).save()

#         #     pass
            
#         # print('instance.employee_id====>>> ',instance.employee_id)
#         # print(app_models.ProductivityMetrics.objects.get(employee_id=instance.employee_id))
#         # pass
#         # print(instance.productivity_metrics , instance.quality_metrics , instance.timeliness_score)
#         # if instance.productivity_metrics and instance.quality_metrics and instance.timeliness_score:
#         #     app_models.ScoreTable(employee_id=instance.employee_id,score=1000).save()
#     else:
#         p=app_models.ProductivityMetrics.objects.get(employee_id=instance.employee_id).productivity_metrics
#         q=app_models.QualityMetrics.objects.get(employee_id=instance.employee_id).quality_score
#         t=app_models.TimelinessMetrics.objects.get(employee_id=instance.employee_id).timeliness_score
#         data = app_models.Weights.objects.all()[0]
#         if p and q and t:
#             score = ((p * data.productivity_per_cent)/100)+((q*data.quality_per_cent)/100)+((t*data.timeliness_per_cent)/100)
#             app_models.ScoreTable(employee_id=instance.employee_id,score=score).save()
#         print('instance.employee_id====>>> ',instance.employee_id)
        
#         # print(instance.productivity_metrics , instance.quality_metrics , instance.timeliness_score)
#         # if instance.productivity_metrics and instance.quality_metrics and instance.timeliness_score:
#         #     app_models.ScoreTable(employee_id=instance.employee_id,score=1000).save()
#         # print('instance productivity_metrics ===updated',instance.employee_id)


# # @receiver(post_save,sender=app_models.ProductivityMetrics)
# # def productivity_extractor(sender,instance,created,**kwargs):
# #     print('from signals = ',instance.user_type)
# #     print(instance)
# #     if created:
# #         if instance.user_type == 'super_user':
# #             # print(ap)
# #             pass
# #             # print('saving new stafff')
# #             # # add this user/instance details to staff table
# #             # name=instance.full_name
# #             # mobile = instance.mobile
# #             # email=instance.email
# #             # user_type=instance.user_type
# #             # # created_at=instance.created_at
# #             # # updated_at=instance.modified_at
# #             # instanse = api_models.Staff(name=name,mobile=mobile,email=email,user_type=user_type)
# #             # instanse.save()
# #         if instance.user_type is not None:
# #             # send email and password to any type of user through EMAIL
# #             pass
