(function(){
  var d = {
    time: new Date().toISOString(),
    page: location.pathname + location.search,
    ref: document.referrer || '',
    ua: navigator.userAgent
  };
  try { navigator.sendBeacon('/api/track', JSON.stringify(d)); } catch(e) {}
})();