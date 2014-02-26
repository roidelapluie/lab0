from tastypie.api import Api
from resources import UserResource, HostResource

api_v1 = Api(api_name='v1')
api_v1.register(UserResource())
api_v1.register(HostResource())
