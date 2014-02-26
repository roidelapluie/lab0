import requests
from lab0.settings import FOREMAN_URL, FOREMAN_USERNAME, FOREMAN_PASSWORD, DEBUG, FOREMAN_SMART_CLASS_PARAMETERS, FOREMAN_COMPUTE_RESOURCES_WITH_CONSOLE, FOREMAN_HOSTGROUPS
if DEBUG:
    import json

class ForemanException(Exception):
        pass

class Foreman:
    def _query(self, query, action='GET', params=None, data=None):
        url = '%s/api/%s' % (FOREMAN_URL, query)
        if DEBUG:
            print 'Request %s, method %s' % (url, action)
            print 'Params', params
            print 'Data', data
        if action == 'GET':
            r = requests.get(url, auth=(FOREMAN_USERNAME, FOREMAN_PASSWORD), verify=False, \
                headers={'Accept': 'application/json; version=2'})
        if action == 'PUT':
            r = requests.put(url, auth=(FOREMAN_USERNAME, FOREMAN_PASSWORD), data=data, verify=False, \
                headers={'Accept': 'application/json; version=2', 'Content-Type': 'application/x-www-form-urlencoded'})
        if action == 'POST':
            r = requests.post(url, auth=(FOREMAN_USERNAME, FOREMAN_PASSWORD), data=data, verify=False, \
                headers={'Accept': 'application/json; version=2', 'Content-Type': 'application/x-www-form-urlencoded'})
        json_data = r.json()
        if DEBUG:
            print json_data, data
        if isinstance(json_data, dict) and json_data.has_key('error'):
            raise ForemanException(json_data['error']['message'])
        if isinstance(json_data, dict) and json_data.has_key('message'):
            raise ForemanException(json_data['message'])
        if r.status_code == 200:
            if DEBUG:
                print 'Response:'
                print json.dumps(json_data, sort_keys=True,
                           indent=4, separators=(',', ': '))
            return json_data

    # Workaround until 1.4
    def get_hosts(self):
        hosts = self._query('hosts?per_page=1999')
        data = []
        for host in hosts:
            data.append(self.get_host(host['host']['name']))
        return data

    def get_smart_variables(self, hostname):
        parameters = {}
        for parameter in FOREMAN_SMART_CLASS_PARAMETERS:
            parameter_dict = FOREMAN_SMART_CLASS_PARAMETERS[parameter]
            parameter_id = parameter_dict['id']
            parameter_label = parameter_dict['label']
            parameters[parameter_id] = {}
            parameters[parameter_id]['label'] = parameter_label
            parameters[parameter_id]['value'] = ''
            parameters[parameter_id]['override_id'] = ''
        smart_parameters = self._query('hosts/%s/smart_class_parameters' % (hostname))

        for parameter in smart_parameters['smart_class_parameters']:
            parameter_id = parameter['id']
            if parameter_id in parameters:
                for value in parameter['override_values']:
                    if value['match'] == 'fqdn=%s' % hostname:
                        parameters[parameter_id]['value'] = value['value']
                        parameters[parameter_id]['override_id'] = value['id']
                if parameters[parameter_id]['value'] == '':
                    parameters[parameter_id]['value'] = parameter['default_value']
        return parameters

    def _get_hostgroups_id(self):
        data = []
        for hostgroup in FOREMAN_HOSTGROUPS:
            data.append(hostgroup['id'])
        return data

    def get_host(self, name):
        data = self._query('hosts/%s' % name)
        parameters = self.get_smart_variables(name)
        data['host']['parameters'] = parameters
        data['host']['hostgroups'] = FOREMAN_HOSTGROUPS
        if data['host']['compute_resource_id'] in FOREMAN_COMPUTE_RESOURCES_WITH_CONSOLE:
            data['host']['console_url']='%s/hosts/%s/console' % (FOREMAN_URL, name)
        return data['host']

    def update_host(self, bundle):

        if not bundle.hostgroup_id in self._get_hostgroups_id():
            raise ForemanException('Not allowed to change the hostgroup')

        data = []
        if bundle.build:
            data.append("host[build]=true")
        else:
            data.append("host[build]=false")

        data.append("host[hostgroup_id]=%s" % bundle.hostgroup_id)

        data = self._query('hosts/%s' % bundle.name, action='PUT', data="&".join(data))
        for parameter in bundle.parameters:
            parameter_id = parameter
            parameter_value = bundle.parameters[parameter]['value']
            override_id = bundle.parameters[parameter]['override_id']
            if override_id == '':
                self.create_smart_class_parameter(bundle.name, parameter_id, parameter_value)
            else:
                self.update_smart_class_parameter(override_id, bundle.name, parameter_id, parameter_value)
        return data['host']

    def create_smart_class_parameter(self,hostname, parameter_id, parameter_value):
        data = []
        data.append('override_value[match]=fqdn=%s' % hostname)
        data.append('override_value[value]=%s' % parameter_value)
        self._query('smart_class_parameters/%s/override_values' % parameter_id, action='POST', data="&".join(data))

    def update_smart_class_parameter(self, override_id, hostname, parameter_id, parameter_value):
        data = []
        data.append('override_value[match]=fqdn=%s' % hostname)
        data.append('override_value[value]=%s' % parameter_value)
        self._query('smart_class_parameters/%s/override_values/%s' % (parameter_id, override_id), action='PUT', data="&".join(data))

    def get_hostnames_by_user(self, username):
        hosts = self._query('hosts?search=user.login=%s' % username)
        data = []
        for host in hosts:
            data.append(host['host']['name'])
        return data

    def get_hosts_by_user(self, username):
        hosts = self._query('hosts?search=user.login=%s' % username)
        data = []
        for host in hosts:
            data.append(self.get_host(host['host']['name']))
        return data

