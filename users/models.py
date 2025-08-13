from django.db import models
from django.contrib.auth.models import AbstractUser

from shared.models import BaseModel

# Create your models here.
ORDINARY_USER,MANAGER,ADMIN=('ordinary_user' , 'manager', 'admin')
VIA_PHONE,VIA_EMAIL=('via_phone' , 'via_email')
NEW,CODE_VERIFIED,DONE,PHOTO_DONE=('new','code','done','photo_done')



class User(AbstractUser,BaseModel):
    USER_ROLES = (
        (ORDINARY_USER,ORDINARY_USER),
        (MANAGER,MANAGER),
        (ADMIN,ADMIN),
    )
    AUTH_TYPE_CHOICES=(
        (VIA_PHONE,VIA_PHONE),
        (VIA_EMAIL,VIA_EMAIL)
    )
    AUTH_STATUS = (
        (NEW,NEW),
        (CODE_VERIFIED,CODE_VERIFIED),
        (DONE,DONE),
        (PHOTO_DONE,PHOTO_DONE),
    )
    user_roles=models.CharField(max_length=31 , choices=USER_ROLES,default='User')
    auth_type=models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)
    auth_status=models.CharField(max_length=31, choices=AUTH_STATUS,default='Auth')
    email=models.EmailField(unique=True ,null=True,blank=True)
    phone_number=models.CharField(max_length=19,null=True,blank=True,unique=True)
    photo=models.ImageField(null=True,blank=True,upload_to='user_photos/')

    def __str__(self):
        return self.username
