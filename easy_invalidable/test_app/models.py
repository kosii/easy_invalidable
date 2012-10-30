from django.db import models

# Create your models here.

# tf, hogy vannak objektumaid egy oop nyelvben (amik amugy egy az egyben egy adatbazis sorainak felelnek meg)
# mindegyikrol tudod, hogy mikor lett utoljara modositva. az objektumok halmazat diszjunkt halmazokra bontod.
# mindegyik halmazhoz hozzarendeled az utoljara modositott eleme modositasanak idopontjat, es a halmaz 
# elemeinek a szamat (ez a halmaz kulcsa).
# minden egyes lepesben modosithatsz egy elemet(masik halmazba rakas is modositasnak szamit), torolhetsz egyet, vagy
# letrezhatsz egy teljesen ujat (uj elemeknel az utolso modositas ideje a letrehozasanak az ideje)
# a kerdes az, hogy tetszoleges muveletsor utan eloallhat-e az, hogy egy halmazhoz ugyanaz a kulcs 
# tartozik, mint korabban (vagy ket kulonbozo halmazhoz ket kulonbozo idopontban ugyanaz a kulcs tartozik)


class EasilyInvalidableQueryset(models.query.QuerySet):
    @property
    def cache_key(self):
        # we have to put .annotate() to workaround this problem:
        # http://obroll.com/aggregate-count-all-number-on-sliced-queryset-limit-query-django-solved/
        # https://code.djangoproject.com/ticket/12886
        if not hasattr(self, '_cache_key'):
        	aggreagation_result = self.annotate().aggregate(models.Max('_modified_at'), models.Min('_modified_at'), models.Count('pk'))
        	self._cache_key = (aggreagation_result['_modified_at__max'], aggreagation_result['_modified_at__min'], aggreagation_result['pk__count'])
        return self._cache_key


class EasilyInvalidableEmptyQueryset(models.query.EmptyQuerySet):
    @property
    def cache_key(self):
        return (None, None, 0)

class EasilyInvalidableManager(models.Manager):
    ## ha mindenhol ezt hasznaljuk, akkor a relatedmanager-eknek ez lesz a superclass-e,
    ## lsd : db.models.fields.related.py, keress: `superclass` -return

    def get_empty_query_set(self):
        return EasilyInvalidableEmptyQueryset(self.model, using=self._db)

    def get_query_set(self):
        return EasilyInvalidableQueryset(self.model, using=self._db)

    @property
    def cache_key(self):
        return self.get_query_set().cache_key

class EasilyInvalidable(models.Model):
    _created_at = models.DateTimeField(auto_now_add=True)
    _modified_at = models.DateTimeField(auto_now=True)

    objects = EasilyInvalidableManager()

    @property
    def cache_key(self):
        return self._modified_at

    class Meta:
        abstract = True



class Student(EasilyInvalidable):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	birthday = models.DateField()
	def __unicode__(self):
		return u'{pk}: {first_name} {last_name}'.format(pk=self.pk, first_name=self.first_name, last_name=self.last_name)

class Prof(EasilyInvalidable):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)

class Class(EasilyInvalidable):
	name = models.CharField(max_length=255)
	prof = models.ForeignKey(Prof, null=True)
	students = models.ManyToManyField(Student)