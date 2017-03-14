from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.response import Response

from collections import OrderedDict


# Based on http://www.django-rest-framework.org/api-guide/pagination/
# https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/pagination.py
class PostsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "size"

    def get_paginated_response(self, data):
        response = OrderedDict([
            ("query", "posts"),
            ("count", self.page.paginator.count),
            ("size", self.page_size),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("posts", data)
        ])
        if not response["next"]:
            response.pop("next")
        if not response["previous"]:
            response.pop("previous")
        return Response(response)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                self.page_size =  _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

class CommentsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "size"

    def get_paginated_response(self, data):
        response = OrderedDict([
            ("query", "comments"),
            ("count", self.page.paginator.count),
            ("size", self.page_size),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("comments", data)
        ])
        if not response["next"]:
            response.pop("next")
        if not response["previous"]:
            response.pop("previous")
        return Response(response)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                self.page_size =  _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size