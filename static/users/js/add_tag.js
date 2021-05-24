var message = '登録できるタグは10個までです'
var max_length = 30

window.addEventListener('load', function(){
  var add_tag_cnt = 0

  document.getElementById('add_tag_button').addEventListener('click', function(){
    let text = document.getElementById('id_tag').value
    if (text.trim() == '') return;
    if (text.length > max_length) {
      alert('タグは' + max_length + '文字以内です')
      document.getElementById('id_tag').value = ''
      return
    }
    let label = document.createElement('label')
    let cb = document.createElement('input')
    cb.type = 'checkbox'
    cb.name = 'tags[]'
    cb.value = text
    cb.checked = true
    add_tag_cnt += 1
    cb.onclick = function(){
      document.getElementById('show_add_tags_area').removeChild(label)
      add_tag_cnt -= 1
    }
    label.appendChild(cb)
    let txt = document.createTextNode(text)
    label.appendChild(txt)
    document.getElementById('show_add_tags_area').appendChild(label)
    document.getElementById('id_tag').value = ''
    if (add_tag_cnt > 10){
      alert(message)
      document.getElementById('show_add_tags_area').removeChild(label)
      add_tag_cnt -= 1
    }
  })
})