var tastypieTransformResponse = function ($http) {
    return $http.defaults.transformResponse.concat([
        function (data, headers) {
            var result = data.objects;
            result.meta = data.meta;
            return result;
        }
    ])
};

var lab0AppServices = angular.module('lab0AppServices', ['ngResource']);

lab0AppServices.factory('Host', ['$resource', '$http',
    function($resource, $http){
        return $resource('/api/v1/host/:name', {}, {
        query: {
            method:'GET',
            params:{name:''},
            isArray:true,
            transformResponse: tastypieTransformResponse($http)
        },
        save: {
            method:'PUT',
            params:{name:"@name"},
        }
    });
}]);

lab0AppServices.factory('User', ['$resource', '$http',
    function($resource, $http){
        return $resource('/api/v1/user/', {}, {
        query: {
            method:'GET',
            isArray:true,
            transformResponse: tastypieTransformResponse($http)
        },
        login: {
            method:'POST'
        },
        logout: {
            method:'DELETE'
        }
    });
}]);
