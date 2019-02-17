from comments.serializers import CommentListSerializer
from shared.serializers import PageSerializer


class ProductListSerializer(PageSerializer):
    resource_name = 'products'


class ProductDetailsSerializer():
    def __init__(self, product):
        self.data = {
            'success': True,
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'slug': product.slug,
            'comments': CommentListSerializer(product.comments.all(), include_user=True).data,
            'tags': [tag.name for tag in product.tags],
            'categories': [category.name for category in product.categories],
            'image_urls': [image.file_path.replace('\\', '/') for image in product.images]
        }
