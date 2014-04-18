'use strict';

describe('Service: Global', function () {

  // load the service's module
  beforeEach(module('auctionItemsApp'));

  // instantiate service
  var Global;
  beforeEach(inject(function (_Global_) {
    Global = _Global_;
  }));

  it('should do something', function () {
    expect(!!Global).toBe(true);
  });

});
