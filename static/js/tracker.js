(function(){
  function pad(n){return n<10?'0'+n:''+n}
  var now=new Date()
  var tz=-now.getTimezoneOffset()
  var tzH=Math.floor(Math.abs(tz)/60)
  var tzM=Math.abs(tz)%60
  var offsetSign=tz>=0?'+':'-'
  var time=now.getFullYear()+'-'+pad(now.getMonth()+1)+'-'+pad(now.getDate())+'T'+
    pad(now.getHours())+':'+pad(now.getMinutes())+':'+pad(now.getSeconds())+
    offsetSign+pad(tzH)+':'+pad(tzM)
  var d={time:time,page:location.pathname+location.search,ref:document.referrer||'',ua:navigator.userAgent}
  try{navigator.sendBeacon('/api/track',JSON.stringify(d))}catch(e){}
})();