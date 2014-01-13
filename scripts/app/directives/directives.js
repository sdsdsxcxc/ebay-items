myApp.directive("masonry", function($parse, $timeout) {
    return {
      restrict: 'AC',
      link: function (scope, elem, attrs) {
          elem.masonry({ visibleStyle: { opacity: 1, transform: 'scale(1)' } , itemSelector: '.masonry-item', isFitWidth: true,  columnWidth: 240});
      },
      controller : function($scope,$element){
          var bricks = [];
          this.appendBrick = function(child, brickId, waitForImage){
              function addBrick() {
                  $element.masonry('appended', child, true);
                  // If we don't have any bricks then we're going to want to 
                  // resize when we add one.
                  if (bricks.length === 0) {
                      $timeout(function(){
                          $element.masonry('resize');  
                      });  
                  }
                
                  // Store the brick id
                  var index = bricks.indexOf(brickId);
                  if (index === -1) {
                      bricks.push(brickId);
                  }
              }
            
              if (waitForImage) {
                  child.imagesLoaded(addBrick);      
              } else {
                  addBrick();
              }
          };

          // Removed bricks - we only want to call masonry.reload() once
          // if a whole batch of bricks have been removed though so push this
          // async.
          var willReload = false;
          function hasRemovedBrick() {
              if (!willReload) {
                  willReload = true;
                  $scope.$evalAsync(function(){
                      willReload = false;
                      $element.masonry("destroy");
                      $element.masonry({ itemSelector: '.masonry-item', 
                          isFitWidth: true,
                          columnWidth: 240});
                  });
              }
          }

          this.removeBrick = function(brickId){
              hasRemovedBrick();
              var index = bricks.indexOf(brickId);
              if (index != -1) {
                  bricks.splice(index,1);
              }
          };
      }
    };     
});

myApp.directive('masonryItem', function ($compile) {
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
});



