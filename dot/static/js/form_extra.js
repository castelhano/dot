function mask_number(e,t){
  let v = t.value.replace('.','');
  let l = v.length;
  if(isNaN(parseInt(t.value.charAt(t.value.length - 1)))){t.value = t.value.substr(0,t.value.length - 1)}
  else{if(l > 3){if(l < 7){t.value = v.substr(0,l - 3) + '.' + v.substr(l - 3,3);}else if(t.value.length > 7){t.value = t.value.substr(0,6) + t.value.substr(7,1);}}}
}