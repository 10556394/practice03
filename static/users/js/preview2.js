
/* 画像登録時のプレビュー機能 */
window.addEventListener('DOMContentLoaded', function(){
  var photo_form_cnt = document.getElementsByClassName('photo_article_form2').length

  for (let i=0; i<photo_form_cnt; i++){
    document.getElementById('id_form-' + i + '-image').addEventListener('change', function(e){
      var url = URL.createObjectURL(e.target.files[0])
      var element = document.getElementById('image_as_article_form2_' + (i+1))
      element.src = url
      element.style.opacity = 1
    })
  }
})

/* is_best選択時のアクション */
window.addEventListener('DOMContentLoaded', function(){
  var form_cnt = document.getElementsByClassName('photo_article_form2').length

  for (let i=0; i<form_cnt; i++){
    document.getElementById('id_form-' + i + '-is_best').addEventListener('change', function(){
      /* ここに処理を記載する */
    })
  }
})