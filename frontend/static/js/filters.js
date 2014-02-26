var lab0AppFilters = angular.module('lab0AppFilters', []);

lab0AppFilters.filter('selectEmpty', function() {
    return function(items) {
        var filtered = []
        angular.forEach(items, function(item){
            if (item.value=='' && item.force != 1){
                filtered.push(item);
            }
        })
        return filtered;
    };
});
lab0AppFilters.filter('selectNonEmpty', function() {
    return function(items) {
        var filtered = []
        angular.forEach(items, function(item){
            if (item.value!='' || item.force==1){
                filtered.push(item);
            }
        })
        return filtered;
    };
});
