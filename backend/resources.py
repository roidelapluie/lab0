from tastypie.resources import Resource
from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from tastypie import fields
from foreman import Foreman
from django.contrib.auth import authenticate, login, logout

class ApiException(Exception):
        pass

class HostObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class HostResource(Resource):

    name = fields.CharField(attribute='name')
    puppet_status = fields.IntegerField(attribute='puppet_status')
    build = fields.BooleanField(attribute='build')
    console_url = fields.CharField(attribute='console_url', null=True, readonly=True)
    parameters = fields.ApiField(attribute='parameters', null=True)
    hostgroups = fields.ApiField(attribute='hostgroups', null=True)
    hostgroups_id = fields.ApiField(attribute='hostgroups_id', null=True)
    hostgroup_id = fields.CharField(attribute='hostgroup_id', null=True)

    def __init__(self, *args, **kwargs):
        super(HostResource, self).__init__(*args, **kwargs)
        self.foreman = Foreman()

    class Meta:
        resource_name = 'host'
        object_class = HostObject
        authorization = Authorization()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs={}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.name
        else:
            kwargs['pk'] = bundle_or_obj.name

        return kwargs

    def get_object_list(self, request):
        #TODO: check if anon
        if request.user:
            query = self.foreman.get_hosts_by_user(request.user.username)
            results = []
            for host in query:
                new_host = HostObject(initial=host)
                results.append(new_host)
            return results
        return []

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        host = self.foreman.get_host(kwargs['pk'])
        return HostObject(initial=host)

    def obj_create(self, bundle, **kwargs):
        pass

    def put_detail(self, request, **kwargs):

        hostnames = self.foreman.get_hostnames_by_user(request.user.username)
        if kwargs['pk'] not in hostnames:
            raise ApiException('Permission denied')

        return super(HostResource,self).put_detail(request, **kwargs)

    def obj_update(self, bundle, **kwargs):
        bundle.obj = HostObject(initial=kwargs)
        bundle = self.full_hydrate(bundle)

        self.foreman.update_host(bundle.obj)

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login']

    def get_object_list(self, request):
        if request.user.is_active:
            return [request.user]
        return []

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_get(self, bundle, **kwargs):
        pass

    def delete_list(self, request, **kwargs):
        logout(request)

    def post_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        data = self.alter_deserialized_detail_data(request, deserialized)
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            if user.is_active:
                login(request,user)
        else:
            raise ApiException('Bad username or password.')


    def obj_update(self, bundle, **kwargs):
        pass

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass
