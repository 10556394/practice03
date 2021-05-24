
var photo_cnt = document.getElementsByClassName('article_photo_box').length
var host = window.location.host
var loct = location.protocol + '//'

/* アルバムのハートマーク処理：アルバム登録していたら、青いハートは非表示にする */
window.onload = function(){
  for (let i=1; i<=photo_cnt; i++){
    if(document.getElementById('link_to_album_show' + i) != null ){
      document.getElementById('link_to_album_regist' + i).style.display = 'none'
    }
  }
}

/* アルバム登録の非同期処理 */
for (let i=1; i<=photo_cnt; i++){
  document.getElementById('link_to_album_regist' + i).addEventListener('click', function(){
    var photo_id = document.getElementById('invisible_tag_for_get_photo_id' + i).textContent
    var article_id = document.getElementById('for_article_regist_asynchronous').textContent
    var path = '/users/album_regist/'
    var url = loct + host + path + photo_id + '/' + article_id

    var XHR = new XMLHttpRequest;
    XHR.open('GET', url)
    XHR.send()

    XHR.onreadystatechange = function(){
      if (XHR.readyState == 4 && XHR.status == 200){
        document.getElementById('link_to_album_regist' + i).style.display = 'none'
        document.getElementById('layzy_love_red' + i).style.display = 'block'
        element = document.getElementById('layzy_love_commit_message' + i)
        element.style.display = 'block'
        setTimeout(function(){
          element.classList.add('fadeout')
        }, 1000)

        setTimeout(function(){
          element.style.display = 'none'
        }, 3000)
      }
    }
  })
}
