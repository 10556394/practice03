
var is_opend = false

document.getElementById('open_tag_regits_form').addEventListener('click', function(){

  var tag_cnt = document.getElementsByClassName('tag').length
  if (tag_cnt >= 10){
    alert('これ以上タグ付けできません')
    exit
  }

  if (is_opend == false){
    document.getElementById('opened_tag_regist_form').style.display = 'block'
    is_opend = true
  } else {
    document.getElementById('opened_tag_regist_form').style.display = 'none'
    is_opend = false
  }
})

var tag_cnt = document.getElementsByClassName('tag').length
var is_del_show = false

document.getElementById('show_delete_checkbox').addEventListener('click',function(){
  if (is_del_show == false){
    for (let i=1; i<=tag_cnt; i++){
      document.getElementById('checkbox_for_tag_delete' + i).style.display = 'block'
      document.getElementById('submit_button_to_tag_delete').style.display = 'block'
      document.getElementById('sharp_as_tag_landmark' + i).style.display = 'none'
    }
    is_del_show = true
  } else {
    for (let i=1; i<=tag_cnt; i++){
      document.getElementById('checkbox_for_tag_delete' + i).style.display = 'none'
      document.getElementById('submit_button_to_tag_delete').style.display = 'none'
      document.getElementById('sharp_as_tag_landmark' + i).style.display = 'block'
    }
    is_del_show = false
  }
})