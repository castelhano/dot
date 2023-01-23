if(document.getElementById('user_list_options').classList.contains('show')){
  if(e.key.toLowerCase() == 's'){e.preventDefault();try{document.getElementById('change_password_link').click()}catch(err){}}
  else if(e.key.toLowerCase() == 'a'){e.preventDefault();try{document.getElementById('shortcut_link_list').click()}catch(err){}}
  else if(e.key.toLowerCase() == 'd'){e.preventDefault();try{document.getElementById('docs').click()}catch(err){}}
}