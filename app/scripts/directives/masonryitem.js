'use strict';

angular.module('auctionItemsApp')
  .directive('masonryItem', [function () {
    return {
        restrict: 'AC',
        require : '^masonry',
        link: function (scope, elem, attrs, MasonryCtrl) {
            elem.imagesLoaded(function () {
                MasonryCtrl.appendBrick(elem, scope.$id, true);
            });

            scope.$on("$destroy",function(){
                MasonryCtrl.removeBrick(scope.$id);
            });
        }
    };
  }]);
