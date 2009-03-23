from django.db import models

# Create your models here.

class Boo(models.Model):
    title = models.CharField(max_length=20)
    slug = models.SlugField()
    class Meta:
        unique_together = ('title', 'slug')

class Foo(models.Model):
    boo = models.ForeignKey(Boo)
    boo2 = models.ForeignKey(Boo, related_name="foo2_set")
