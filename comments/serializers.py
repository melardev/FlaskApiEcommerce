from shared.serializers import PageSerializer


class CommentListSerializer(PageSerializer):
    resource_name = 'comments'

    def __init__(self, comments_or_pagination, **kwargs):
        if type(comments_or_pagination) == list:
            self.data = [comment.get_summary(**kwargs) for comment in comments_or_pagination]
        else:
            super(CommentListSerializer, self).__init__(comments_or_pagination, **kwargs)


class CommentDetailsSerializer():
    def __init__(self, comment, include_user=False, include_product=False):
        self.data = {'success': True}
        self.data.update(comment.get_summary(include_product, include_user))
