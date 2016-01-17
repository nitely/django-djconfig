# -*- coding: utf-8 -*-

from django.db import models


class ChoiceModel(models.Model):

    name = models.CharField(max_length=75)
