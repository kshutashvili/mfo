from django.db import models


class Token(models.Model):
	token = models.CharField('token',
							 max_length=64)

	def __unicode__(self):
		return self.token

