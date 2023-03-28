from datetime import datetime
from datetime import time
from datetime import timedelta
import hmac
import hashlib
from io import BytesIO
import locale
import json
from mimetypes import MimeTypes
import os
import orjson
import re
import string
import subprocess
from PIL import Image, ImageOps
import random
import requests
import traceback
from typing import Optional
from uuid import UUID
import urllib
import urllib.request

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from django.utils import timezone

import config.models as config_models
from config.utils import get_setting

from application.celery import app


def is_time_in_period(start_time, end_time, now_time):
    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    else:
        # Over midnight:
        return now_time >= start_time or now_time <= end_time


def log_message(message=None, exception: Optional[Exception] = None):
    if not settings.DEBUG:
        return

    if isinstance(message, list):
        [print(m) for m in message]
    elif isinstance(message, str):
        print(message)

    if exception is not None:
        print(traceback.format_exc())


def is_now_work_time(start_hour=7, start_min=45, end_hour=17, end_min=0, week_max_days=4):
    '''
    verifica se a hora corrente (now) está dentro de um período de trabalho
    da empresa, ou seja, se a data/hora atual é um horário de expediente.
    '''
    _now = timezone.now()
    if _now.weekday() <= week_max_days:
        '''
        dia entre 0 e 4 é dia de expediente (seg-sex)
        5 é sábado e 6 domingo.
        '''
        hour_start = time(start_hour, start_min)
        hour_end = time(end_hour, end_min)
        return is_time_in_period(hour_start, hour_end, _now.time())
    else:
        return False


def get_current_site_url(append_path=None, uses_admin=True):
    site = config_models.Site.objects.get(pk=1)
    base_url = site.url_admin if uses_admin else site.url_site

    if append_path is not None:
        return "%s/%s/" % (base_url, append_path)

    return "%s/" % (base_url)


def download_file(file_url, destination_file_name):
    try:
        # Check whether the specified path exists or not
        path = os.path.dirname(destination_file_name)
        if not os.path.exists(path):
            os.makedirs(path)

        response = requests.get(file_url, allow_redirects=True)
        if response.status_code == 404:
            raise Exception("Arquivo não disponível para a url: {}. O servidor remoto retornou o status 404.".format(file_url))

        response = urllib.request.urlopen(file_url)
        file = open(destination_file_name, 'wb')
        file.write(response.read())
        file.close()

        return os.path.getsize(destination_file_name) > 0
    except Exception as e:
        log_message([
            "Erro ao tentar fazer o download do documento a seguir:",
            "destination_file_name: %s" % (destination_file_name),
            "file_url: %s" % (file_url),
            str(e)
        ])

        return False


def capitalize_name(name: str) -> str:
    capital_name = []
    ignore = ['dos', 'das', 'des', 'dus',
              'do', 'da', 'de', 'di', 'du']

    for n in name.split(" "):
        if n.lower() in ignore:
            capital_name.append(n.lower())
        else:
            capital_name.append(n.capitalize())
    return " ".join(capital_name)


def random_code(range=6, letter_only=False):
    if letter_only:
        chars = (random.choice(string.ascii_letters) for x in range(range))
        return ''.join(chars)

    idx = 0
    code = []
    while idx < range:
        if idx % 2 > 0:
            code.append(str(random.randrange(0, 9)))
        else:
            code.append(random.choice(string.ascii_uppercase))
        idx += 1
    return "".join(code)


def random_activation_account_code():
    randomlist = random.sample(range(10, 100), 3)
    return "".join(map(str, randomlist))


def safe_str(obj):
    try:
        return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')


def strfy_json(data) -> str:
    if data is None:
        return ""

    if isinstance(data, str):
        return data

    try:
        data_dict = dict(data)
    except:
        data_dict = data

    # other option
    """
    safe_dict = {}
    for k, v in data_dict.items():
        for g, h in v.items():
            safe_dict[safe_str(g)] = safe_str(h)
    return str(json.dumps(safe_dict, ensure_ascii=False))
    """

    try:
        return str(json.dumps(data_dict, ensure_ascii=False))
    except:
        try:
            return json.dumps(data_dict, ensure_ascii=False).encode('ascii', 'ignore').decode('ascii')
        except:
            return str(orjson.dumps(data_dict, option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY))


def get_time_threshold(days: int):
    time_threshold = timezone.now() - timedelta(days=days)
    time_threshold = time_threshold.replace(minute=0, hour=0)
    return time_threshold


def compress_image(img_obj, quality=60, megabyte_limit=1.0):
    if img_obj is not None and img_obj.name is not None and len(img_obj.name) > 0:
        filesize = img_obj.file.size

        # se a imagem for maior que megabyte_limit aplica a redução do tamanho
        if filesize > megabyte_limit*1024*1024:
            thumb_io = BytesIO()

            img = Image.open(img_obj)
            format = img_obj.name.split('.')[-1].upper()

            if format == 'PNG':
                format = 'JPEG'
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new(img.mode[:-1], img.size, 'white')
                    background.paste(img, img.split()[-1])
                    img = background
                elif img.mode not in ('RGB',):
                    img = img.convert('RGB')
            elif format == 'JPG':
                format = 'JPEG'

            img.save(thumb_io, format=format, optimize=True, quality=quality)

            return File(thumb_io, name=img_obj.name)
    return img_obj


def apply_vehicle_image_restriction(image):
    image_width, image_height = get_image_dimensions(image)
    if image_width is None or image_height is None:
        raise ValidationError('As imagens dos Seminovos não podem ser nulas ou inválidas. Utilize os formatos png ou jpg ou webp.')
    if image_width < settings.SEMINOVO_IMAGE_MINIMUM_WIDTH or image_height < settings.SEMINOVO_IMAGE_MINIMUM_HEIGHT:
        raise ValidationError("As imagens dos Seminovos precisam ter no mínimo %dx%dpx de dimensões. Os formatos aceitos são jpg ou png ou webp." % (settings.SEMINOVO_IMAGE_MINIMUM_WIDTH, settings.SEMINOVO_IMAGE_MINIMUM_HEIGHT))


def apply_vehicle_brand_image_restriction(image):
    image_width, image_height = get_image_dimensions(image)
    if image_width is None or image_height is None:
        raise ValidationError('A imagem da marcas de veículo não pode ser nulas ou inválidas. Utilize os formatos png ou jpg ou webp.')
    if image_width < 256 or image_height < 256:
        raise ValidationError("A imagem da marca de veículo deve ter no mínimo 256x256px de dimensões. Os formatos aceitos são jpg ou png ou webp.")


# ver mais sobre resize de imagens no python:
# https://stackoverflow.com/questions/273946
# /how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
def apply_image_defaults(img_obj, needed_width, needed_height, quality=40):
    # check if image ins valid to apply the customization
    format = img_obj.name.split('.')[-1].upper().strip()
    if format == 'GIF':
        return img_obj

    if img_obj is not None and img_obj.name is not None and len(img_obj.name) > 0:
        filesize = img_obj.file.size

        # se a imagem for maior que 100kb aplica a redução e padronização
        # Obs: img_obj.file.size o valor é em bytes!
        if filesize > 10000:
            needed_aspect_ratio = needed_width/needed_height

            img = Image.open(img_obj)

            # corrige autorotate da imagem
            img = ImageOps.exif_transpose(img)

            bytes_io = BytesIO()
            orignal_img_width, orignal_img_height = img.size
            aspect_ratio = orignal_img_width/orignal_img_height

            if format == 'PNG':
                format = "JPEG"
                if img.mode in ('RGBA', 'RGB', 'LA', 'P'):
                    img = img.convert('RGB')
            elif format == 'JPG':
                format = "JPEG"

            if needed_aspect_ratio == aspect_ratio:
                img = img.resize((needed_width, needed_height), Image.ANTIALIAS)
            else:
                new_width = round(needed_height * aspect_ratio)
                new_height = round(needed_width / aspect_ratio)

                if new_width < needed_width:
                    new_width = needed_width
                if new_height < needed_height:
                    new_height = needed_height

                img = img.resize((new_width, new_height), resample=Image.LANCZOS)

            img.save(bytes_io, format=format, optimize=True, quality=quality, quality_mode='dB', quality_layers=[41])

            format = format.lower()
            new_file_name = ".".join(img_obj.name.split('.')[:-1])
            new_file_name = "{}.{}".format(new_file_name, 'jpg' if format == 'jpeg' else format)

            return File(bytes_io, name=new_file_name)
    return img_obj


def can_send_notification():
    value = get_setting("CAN_SEND_NOTIFICATION")
    return value.enabled if value.enabled is not None else True


def can_send_admin_notification():
    value = get_setting("CAN_SEND_ADMIN_NOTIFICATION")
    return value.enabled if value.enabled is not None else True


def can_sync_locavia():
    value = get_setting("API_LOCAVIA_SYNC_ENABLED")
    return value.enabled if value.enabled is not None else True


def can_check_api_exato():
    value = get_setting("API_EXATO_DIGITAL_ENABLED")
    return value.enabled if value.enabled is not None else True


def can_send_contrato_digital():
    value = get_setting("API_D4SIGN_ENABLED")
    return value.enabled if value.enabled is not None else True


def can_call_celery(who_requesting: str):
    try:

        app.broker_connection().ensure_connection(max_retries=2)
        return True
    except:
        message = "Failed to connect to celery broker: {}.".format(who_requesting)
        if settings.DEBUG:
            print("** Error **")
            print(message)

        try:
            # TODO precisa rever esse import
            from notification.celerytasks import post_sync_slack_message
            post_sync_slack_message(message, "backend-errors")
        except:
            pass

        return False


def default_render_template_email(append_template_path, message_args, site=None):
    if site is None:
        site = config_models.Site.objects.get(pk=1)

    email_params = {
        # "logo_url": site.logomarca,
        "logo_url": "https://res.cloudinary.com/realizadigital/image/upload/v1650676220/logomarcas/logomarca-realiza-100px_b8xofv.png",
        "site_url": site.url_site,
        "site_name": site.name_site,
        "realiza_address": site.endereco,
        "current_year": datetime.today().year,
    }

    template_base = settings.BASE_DIR + "/templates/email/base_template.html"
    template = "{}.html".format(append_template_path)

    message_content_str = render_to_string(template, {**email_params, **message_args})
    message_content_arg = {'message_content': message_content_str}

    html_message = render_to_string(template_base, {**email_params, **message_content_arg})

    return html_message, email_params


def format_currency(value):
    locale_currency = ""

    try:
        if settings.ENVIRONMENT == "production":
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        else:
            locale.setlocale(locale.LC_ALL, 'C')

        locale_currency = locale.currency(float(value), grouping=True, symbol=True)
    except:
        pass

    if len(locale_currency) == 0:
        locale_currency = "R$ {}".format(float(value)).strip()
        if locale_currency[-2:-1] == ".":
            return "{}0".format(locale_currency)
    elif locale_currency[-2:] == "R$":  #  se o cifrão tiver repetido
        return "R$ {}".format(locale_currency[:-2]).strip()

    return locale_currency.strip()


def default_metadata(initial_values={}):
    return {}.update(initial_values)


def file_mimetype(file_name):
    try:
        mime = MimeTypes()
        url = urllib.pathname2url(file_name)
        return mime.guess_type(url)
    except:
        if file_name:
            if file_name.endswith(".jpg"):
                return 'image/jpeg'
            elif file_name.endswith(".png"):
                return 'image/png'
            elif file_name.endswith(".gif"):
                return 'image/gif'
            elif file_name.endswith(".webp"):
                return 'image/gif'

    return 'unknow/unknow'


def create_sha256_signature(key: str, message: str):
    signature = hmac.new(
        key.encode('utf-8'), message.encode('utf-8'),
        hashlib.sha256).hexdigest()

    return signature


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def get_current_commit_hash(from_deploy=False):
    if from_deploy == False:
        _command = "cd {} && git rev-parse HEAD".format(settings.BASE_DIR)
    else:
        _command = "cd {} && cd realizadigital.deploy && git rev-parse HEAD".format(settings.ROOT_DIR)

    p = subprocess.Popen(_command, stdout=subprocess.PIPE, shell=True)
    hash_id = p.communicate()[0].strip().decode('utf-8')
    return hash_id


def create_log(file_name: str, content: str, custom_dir=None):
    log_dir = settings.LOG_DIR

    # fir custom dir passed add to destination directory
    if custom_dir is not None:
        log_dir += custom_dir

    try:
        # create the destination if not exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        if settings.DEBUG:
            print("****************************************")
            print("Atenção para esse erro:")
            print(str(e))
            print("****************************************")

    # fix: .log.log in file name
    if file_name[-4:] == ".log":
        file_name = file_name[:-4]

    file_name = "{}/{}.log".format(log_dir, file_name)

    try:
        f = open(file_name, 'w', encoding='utf8')
        f.write(content)
        f.close()
    except Exception as e:
        if settings.DEBUG:
            print("****************************************")
            print("Atenção para esse erro:")
            print(str(e))
            print("****************************************")

    return file_name


def model_to_dict(instance, include=None, exclude=None):
    fields = instance._meta.concrete_fields
    if include is not None:
        return {f.attname: getattr(instance, f.attname) for f in fields if f.name in include}
    if exclude is not None:
        return {f.attname: getattr(instance, f.attname) for f in fields if f.name not in exclude}
    return {f.attname: getattr(instance, f.attname) for f in fields}


def html_response(request, template_name, status_code, context = {}):
	template = loader.get_template('%s/templates/%s' % (settings.BASE_DIR, template_name))
	response = template.render(context, request)

	response = HttpResponse(response)
	response.status_code = status_code

	return response


def consulta_cep(cep):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"}

    try:
        url = "https://viacep.com.br/ws/{}/json/".format(re.sub("[^0-9]", "", cep))
        request_response = requests.get(url=url, headers=headers, timeout=30, verify=True)
        endereco = request_response.json()

        return {
            "logradouro": endereco["logradouro"],
            "bairro": endereco["bairro"],
            "cidade": endereco["localidade"],
            "uf": endereco["uf"]}
    except:
        return {
            "logradouro": "",
            "bairro": "",
            "cidade": "",
            "uf": ""}


def sanitize_except_message(msg: str) -> str:
    try:
        s = msg + ""
        special_characters = ['#', '$', '%', '&', '@', '[', ']', '\'']
        for i in special_characters:
            s = s.replace(i,'')
        return s
    except:
        return msg
