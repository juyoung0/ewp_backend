app : mongo/view

DATABASES = {
    'mongo':{
        'ENGINE': 'django.db.backends.',
        'NAME': 'kewp_10m',
        'HOST': 'mongodb://kewp:kewp@wilkes.unist.ac.kr/kewp',
        'PORT': 27017,
    }
}