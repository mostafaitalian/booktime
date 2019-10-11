import logging
from io import BytesIO

from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from PIL import Image

from .models import Basket, Order, OrderLine, ProductImage, User

logger = logging.getLogger(__name__)
THUMBNAIL_SIZE = (100,100)
@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info('create image thumbnail for product {}'.format(instance.product.name))
    image = Image.open(instance.image)
    image = image.convert('RGB')
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp = BytesIO()
    image.save(temp, 'JPEG')
    temp.seek(0)
    instance.thumbnail.save(instance.image.name, ContentFile(temp.read()), save=False)
    temp.close()
@receiver(pre_save, sender=ProductImage)
def generate_thumbnaill(sender, instance, **kwargs):
    image = Image.open(instance.image)
    image = image.convert('RGB')
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp1 = BytesIO()
    image.save(temp1, 'JPEG')
    temp1.seek(0)
    instance.thumbnail.save(instance.image.name, ContentFile(temp1.read()), save=False)
    temp1.close()
@receiver(user_logged_in)
def merge_basket_if_logged_in(sender, user, request, **kwargs):
    anonymous_basket = getattr(request, "basket", None) 
    if anonymous_basket:
        try:
            logged_in_basket = Basket.objects.get(user=user, status=10)
            for line in anonymous_basket.lines.all():
                line.basket = logged_in_basket
                line.save()
            anonymous_basket.delete()
            request.basket = logged_in_basket

        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
@receiver(post_save, sender=OrderLine)
def orderline_to_order_status(sender, instance, **kwargs):
    if not instance.order.order_lines.filter(status__lt=OrderLine.SENT).exists():
        instance.order.status = Order.DONE
        instance.order.save()
    if instance.order.order_lines.filter(status=OrderLine.CANCELLED).count() == instance.order.order_lines.all().count():
        instance.order.status = Order.CANCELLED
        instance.order.save()
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_authtoken(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        