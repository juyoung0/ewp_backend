from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


#juyoung 9c3171ede91b2d8ea152bf5bead5282970b598d5
#test aa55f220e71dc2b97e4252ea2bb28255db4db928
#test2 a5d9eb1cd34f373e0a11d2127381490159d9b71e
#admin 0182d13b1098a2125d0f4191b850f55caf215533
#t f8f5fee7b7253a6ff3d7d8568f1434822a382fe9
#t2 11696122c8a6f4aa8783ec179092276f89364a21
#t23 6d15ba980377f045f4ac4da42b9c1f6fc67e1509
#t24444 89eee261aab4d605a7b57adbdd9af3cec7921d94
#t244440 44f5344eebfe89d513e1fbc4849bf5b04a10850f
#abc2 7169e9ec1931796c0f7343070b431a8626922de1
#aa 58a2dcf1e81960012c9e1103d711bdb4d98afc7a
#hi dec8e2ced4c50e764a685ad0b5efdcb7fdbe1ac5
#hello d283d24c10e7e0076525093ad91c629974583b05
