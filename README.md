# django-quill-editor

![PyPI](https://img.shields.io/pypi/v/django-quill-editor)

**django-quill-editor** makes [Quill.js](https://quilljs.com/) easy to use on Django Forms and admin sites

- **No configuration required for static files!**
- The entire code for inserting WYSIWYG editor is less than 30 lines
- It can be used in both admin and Django views

![django-quill-editor](https://raw.githubusercontent.com/LeeHanYeong/django-quill-editor/master/_assets/django-quill-editor-sample.png)

> **Warning**  
> The content entered in django-quill-editor can be used for XSS attacks because it is marked_safe by Django.  
> Only authorized administrators should use it in important projects.
>
> - [XSS](https://docs.djangoproject.com/en/dev/topics/security/#cross-site-scripting-xss-protection)
> - [mark_safe](https://docs.djangoproject.com/en/dev/ref/utils/#django.utils.safestring.mark_safe)

## Live Demo

#### https://quill.lhy.kr/

- Form | https://quill.lhy.kr/posts/create/normal/
- ModelForm | https://quill.lhy.kr/posts/create/
- Form (Initial HTML) | https://quill.lhy.kr/posts/create/normal/html/
- Form (Initial Text) | https://quill.lhy.kr/posts/create/normal/text/
- Admin | https://quill.lhy.kr/admin/login/



## Documentation

The full document is in [https://django-quill-editor.readthedocs.io/](https://django-quill-editor.readthedocs.io/), including everything about how to use the Form or ModelForm, and where you can add custom settings.

Please refer to the **QuickStart** section below for simple usage.



## QuickStart

### Setup

- Install `django-quill-editor` to your Python environment

  > Requires Python 3.7 or higher and Django 3.1 or higher.

  ```shell
  pip install django-quill-editor
  ```

- Add `django_quill` to `INSTALLED_APPS` in `settings.py`

  ```python
  # settings.py
  INSTALLED_APPS = [
      'django.contrib.admin',
      ...
      'django_quill',
  ]
  ```

### Making Model

Add `QuillField` to the **Model class** you want to use.

> 1. App containing models.py must be added to INSTALLED_APPS
> 2. After adding the app, you need to run makemigrations and migrate to create the DB table.

## Run Sample project

Repo: [django-quill-editor-sample](https://github.com/LeeHanYeong/django-quill-editor-sample)

```shell
# Clone repo
git clone https://github.com/LeeHanYeong/django-quill-editor-sample
cd django-quill-editor-sample

# Create virtualenv (I used pyenv, but you can use other methods)
pyenv virtualenv 3.7.5 django-quill
pyenv local django-quill

# Install Python packages
pip install -r requirements.txt
python app/manage.py runserver
```



## Documentation

Documentation for **django-quill-editor** is located at [https://django-quill-editor.readthedocs.io/](https://django-quill-editor.readthedocs.io/)



## Change toolbar configs

Add `QUILL_CONFIGS` to the **settings.py**

If you want to use inline style attributes (`style="text-align: center;"`) instead of class (`class="ql-align-center"`)
, set `useInlineStyleAttributes` to `True`.
It changes the settings only for `align` now. You can check the related
[Quill Docs](https://quilljs.com/guides/how-to-customize-quill/#class-vs-inline).

```python
QUILL_CONFIGS = {
    'default':{
        'theme': 'snow',
        'useInlineStyleAttributes': True,
        'modules': {
            'syntax': True,
            'toolbar': [
                [
                    {'font': []},
                    {'header': []},
                    {'align': []},
                    'bold', 'italic', 'underline', 'strike', 'blockquote',
                    {'color': []},
                    {'background': []},
                ],
                ['code-block', 'link'],
                ['clean'],
            ],
            'imageUploader': {
                'uploadURL': '/admin/quill/upload/',        # You can also use an absolute URL (https://example.com/3rd-party/uploader/)
                'addCSRFTokenHeader': True,
            }
        }
    }
}
```

## Image uploads

If you want to upload images instead of storing encoded images in your database. You need to add `imageUploader` module
to your configuration. If you set a `uploadURL` for this modules, it registers
[quill-image-uploader](https://www.npmjs.com/package/quill-image-uploader) to Quill.
You can add a view to upload images to your storage service. Response of the view must contain `image_url` field.

```python
# urls.py
from django.urls import path
from .views import EditorImageUploadAPIView

urlpatterns = [
   ...
   path('admin/quill/upload/', EditorImageUploadAPIView.as_view(), name='quill-editor-upload'),
   ...
]
```

```python
# You don't have to use Django Rest Framework. This is just an example.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .serializers import EditorImageSerializer


class EditorImageUploadAPIView(CreateAPIView):
    serializer_class = EditorImageSerializer
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        # image_url = handle image upload
        return Response({'image_url': "https://xxx.s3.amazonaws.com/xxx/x.png"}, status=status.HTTP_200_OK)
```

```json
{
  "image_url": "https://xxx.s3.amazonaws.com/xxx/x.png"
}
```

## Usage

Add `QuillTextField` or `QuillJSONField` to the **Model class** you want to use.

```python
# models.py
from django.db import models
from django_quill.fields import QuillField, QuillTextField, QuillJSONField

class QuillPost(models.Model):
    content = QuillField()              # Deprecated. It is same with QuillTextField.
    content = QuillTextField()
    content = QuillJSONField()
```

### Using in admin

Just register the Model in **admin.py** of the app.

```python
from django.contrib import admin
from .models import QuillPost

@admin.register(QuillPost)
class QuillPostAdmin(admin.ModelAdmin):
    pass
```

![admin-sample](https://raw.githubusercontent.com/LeeHanYeong/django-quill-editor/master/_assets/admin-sample.png)

- Add `QuillFormJSONField` to the **Form class** you want to use

## Running the Live Demo project in local

The live demo is a deployment of the **"playground"** package, which is a django application within this library.  
After cloning or downloading the repository, you can try running the live demo locally.

**A Python virtual environment is required to run the project.**

```shell
# [Optional] We recommend that you start after creating a folder for your project.
mkdir ~/projects
cd projects

# Clone repository
git clone git@github.com:LeeHanYeong/django-quill-editor.git

# Go to the project directory and apply the virtual environment
cd django-quill-editor
# [apply venv]

# Go to the playground package
cd playground

# Install requirements
pip install -r requirements.txt

# Run migrate and runserver
python manage.py migrate
python manage.py runserver
```

```python
# forms.py
from django import forms
from django_quill.forms import QuillFormJSONField

class QuillFieldForm(forms.Form):
    content = QuillFormJSONField()
```

After the above operation, the live demo site works at localhost:8000.



## Contributing

As an open source project, we welcome contributions.
The code lives on [GitHub](https://github.com/LeeHanYeong/django-quill-editor)



## Distribution tips (for owners)

### Installation

```shell
# black
brew install black

# pre-commit
brew install pre-commit
pre-commit install
```

### PyPI Release

```shell
poetry install  # Install PyPI distribution packages
python deploy.py
```

### Sphinx docs

```shell
brew install sphinx-doc  # macOS
```

#### Local

```
cd docs
make html
# ...
# The HTML pages are in _build/html.

cd _build/html
python -m http.server 3001
```

 

### docker-compose up

```shell
# local
docker-compose --env-file .deploy/.env.local up --build --force-recreate --remove-orphans
# production
docker-compose --env-file .deploy/.env.production up --build --force-recreate --remove-orphans
```

