from shared.serializers import PageSerializer


class AddressListSerializer(PageSerializer):
    resource_name = 'addresses'


class CommentDetailsSerializer():
    def __init__(self, comment, include_user=False, include_product=False):
        self.data = {'success': True}
        self.data.update(comment.get_summary(include_product, include_user))
