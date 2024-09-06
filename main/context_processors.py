from .models import BackgroundImage

def background_images(request):
    images = BackgroundImage.objects.all().order_by('order')
    return {'background_images': images}