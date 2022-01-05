function updateUrl(uri, key, value) {
  var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
  var separator = uri.indexOf('?') !== -1 ? "&" : "?";
  if (uri.match(re)) {
    return uri.replace(re, '$1' + key + "=" + value + '$2');
  }
  else {
    return uri + separator + key + "=" + value;
  }
}
// USAGE: filter('nome', 'rafael')
function filter(filter, value){location.href = updateUrl(window.location.href, filter, value);}
function urlHasParam(param){return urlParams.has(param);}
function urlParams(){return window.location.search;}
function urlSetFiltersActive(filters){
  for i in filters{
    console.log(i);
  }
}
