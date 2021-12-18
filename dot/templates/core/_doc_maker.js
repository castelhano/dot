editor = document.getElementById('editor');
placeholder = document.getElementById('placeholder');

function editor_keypress(){
  editor.innerHTML = editor.innerHTML.replace(/\[[^\]]*?\]/g, '__');
  editor.innerHTML = editor.innerHTML;
}

function editor_focus(){
  if(editor.innerHTML == '<span id="placeholder" class="text-muted">Editor</span>'){editor.innerHTML = '';}
}

function editor_focusout(){
  if(editor.innerHTML == ''){editor.innerHTML = '<span id="placeholder" class="text-muted">Editor</span>';}
}
// 
// tags = {
//   ""
// }