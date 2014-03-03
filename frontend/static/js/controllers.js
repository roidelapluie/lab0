var lab0AppControllers = angular.module('lab0AppControllers',[]);

function set_error(error,$scope){
 $scope.error=error['data']['error_message'];
}

lab0AppControllers.controller('ForemanCtrl', ['$scope', 'Host', 'User', function ($scope, Host, User) {
    $scope.hosts = Host.query();
    $scope.user = User.query();
    $scope.login_username = "";
    $scope.login_password = "";
    $scope.logout = function(){
        User.logout({},{}, function(){
            $scope.user = User.query();
            $scope.hosts = Host.query();
        });
    }
    $scope.login = function(username, password){
        $scope.error=false;
        User.login({},{'username':username,'password':password}, function(){
            $scope.user = User.query();
            $scope.hosts = Host.query();
        },
        function(e){
            $scope.error = e['data']['error_message'];
        });
    }
    $scope.refreshHost = function(host){
        host.refreshing=true;
        host = host.$get({name: host.name}, null,
        function(e){
            $scope.error = e['data']['error_message'];
        });
    }
    $scope.updateHost = function(host){
        if (host.modified == 1||host.modified==3)
        {
        host.modified += 1;
        }
        host.$save(function (host) {
            host.modified=0;
            host.refreshing=true;
            host = host.$get({name: host.name});
        }, function(e){
            $scope.error = e['data']['error_message'];
        });
    };
}]);
