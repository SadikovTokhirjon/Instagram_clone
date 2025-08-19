import random
import uuid
from datetime import timedelta, timezone

from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

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
    photo=models.ImageField(null=True,blank=True,upload_to='user_photos/',validators=[(FileExtensionValidator(allowed_extensions=['png','jpg','jpeg'])) ])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


    def create_verify_code(self,verify_type):
        code="".join([str(random.randint(0,100)%10) for _ in range(4)])
        UserConfirm.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code,
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username=f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'

            while User.objects.filter(username=temp_username):
                temp_username=f"{temp_username}{random.randint(0,9)}"
            self.username=temp_username


    def chech_email(self):
        if self.email:
            normalize_email=self.email.lower()
            self.email=normalize_email


    def check_password(self):
        if not self.password:
            temp_password=f'password-{uuid.uuid4().__str__().split("-")[-1]}'
            self.password=temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def token(self):
        reflesh=RefreshToken.for_user(self)
        return {
            "access": str(reflesh.access_token),
            "refresh": str(reflesh),
        }


    def clean(self):
        self.chech_email()
        self.check_username()
        self.check_password()
        self.hashing_password()


    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()

        super(User,self).save(*args, **kwargs)







EMAIL_EXPIRE=5
PHONE_EXPIRE=2

class UserConfirm(BaseModel):
    TYPE_CHOICES=(
        (VIA_PHONE,VIA_PHONE),
        (VIA_EMAIL,VIA_EMAIL)
    )
    code=models.CharField(max_length=4)
    verify_type=models.CharField(max_length=31,choices=TYPE_CHOICES)
    user=models.ForeignKey("users.User",models.CASCADE , related_name='verify_codes')
    expiration_time=models.DateTimeField(null=True)
    is_confirmed=models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.verify_type=='VIA_PHONE':
                self.expiration_time=timezone.now()+timedelta(minutes=PHONE_EXPIRE)
            else:
                self.expiration_time=timezone.now()+timedelta(minutes=EMAIL_EXPIRE)
        super(UserConfirm,self).save(*args, **kwargs)