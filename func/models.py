from django.db import models

class RestrBase(models.Model):
    class Meta:
        db_table = 'Restr_Base'

    rid = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 30)
    phone = models.CharField(max_length = 20, null = True)
    bid = models.ForeignKey('BldgBase', db_column = 'bid')
    floor = models.IntegerField(null = True)
    addr = models.TextField(null = True)
    lati = models.FloatField(null = True)
    longi = models.FloatField(null = True)
    distHQ = models.FloatField(null = True)
    distIT = models.FloatField(null = True)
    uptTime = models.DateTimeField()
    avgRating = models.FloatField(default = -1)
    hitScore = models.IntegerField(default = 0)
    referenceURL = models.URLField(null = True)
    thumbnailURL = models.URLField(null = True)
    tag = models.TextField(null = True)

class UserBase(models.Model):
    class Meta:
        db_table = 'User_Base'

    sid = models.CharField(max_length = 20, primary_key = True)
    nickName = models.CharField(max_length = 30)
    regTime = models.DateTimeField()
    lastConnTime = models.DateTimeField()

class UserReview(models.Model):
    class Meta:
        db_table = 'User_Review'
        unique_together = (('sid', 'rid', 'reviewTime'), )

    review_id = models.AutoField(primary_key = True)
    sid = models.ForeignKey(UserBase, db_column = 'sid')
    rid = models.ForeignKey(RestrBase, db_column = 'rid')
    reviewTime = models.DateTimeField()
    rating = models.FloatField()
    reviewText = models.TextField(null = True)

class UserViewHist(models.Model):
    class Meta:
        db_table = 'User_View_Hist'
        unique_together = (('sid', 'rid', 'viewTime'), )

    hist_id = models.AutoField(primary_key = True)
    sid = models.ForeignKey(UserBase, db_column = 'sid')
    rid = models.ForeignKey(RestrBase, db_column = 'rid')
    viewTime = models.DateTimeField()
    staySeconds = models.IntegerField(null = True)

class BldgBase(models.Model):
    class Meta:
        db_table = 'Bldg_Base'

    bid = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 30)
    addr = models.TextField(null = True)
    lati = models.FloatField(null = True)
    longi = models.FloatField(null = True)

class RestrCrawl(models.Model):
    class Meta:
        db_table = 'Restr_Crawl'

    name = models.CharField(max_length = 30, primary_key = True)
    phone = models.CharField(max_length = 20, null = True)
    #bid = models.ForeignKey('BldgBase', db_column = 'bid')
    #floor = models.IntegerField(null = True)
    addr = models.TextField(null = True)
    lati = models.FloatField(null = True)
    longi = models.FloatField(null = True)
    distHQ = models.FloatField(null = True)
    distIT = models.FloatField(null = True)
    uptTime = models.DateTimeField()
    #avgRating = models.FloatField(default = -1)
    #hitScore = models.IntegerField(default = 0)
    referenceURL = models.URLField()
    thumbnailURL = models.URLField(null = True)
    #tag = models.TextField(null = True)
    rid = models.ForeignKey(RestrBase, db_column = 'rid')

class NicknameSrcAdj(models.Model):
    class Meta:
        db_table = 'Nickname_Src_Adj'

    adjective = models.CharField(max_length = 30)
    cnt_used = models.IntegerField(default = 0)
    last_used_time = models.DateTimeField()

class NicknameSrcNoun(models.Model):
    class Meta:
        db_table = 'Nickname_Src_Noun'

    noun = models.CharField(max_length = 30)
    cnt_used = models.IntegerField(default = 0)
    last_used_time = models.DateTimeField()