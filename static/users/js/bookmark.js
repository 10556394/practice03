/*
このスクリプトファイルには、ブックマーク機能に関する処理を記載する
*/

var art_cnt = document.getElementsByClassName('art_box').length
var host = window.location.host
var loct = location.protocol + '//'

/* お気に入りのハートマーク処理：お気に入りしていたら、青いハートは非表示にする */
window.onload = function(){
  for (let i=1; i<=art_cnt; i++){
    if (document.getElementById('is_bookmarked' + i) != null ){
      document.getElementById('to_bookmark' + i).style.display = 'none'
    }
  }
}


/* お気に入り登録の非同期処理 */
var is_XHR = document.getElementById('invisible_tag_for_get_is_XHR').textContent

if (is_XHR == 1){
  for (let i=1; i<=art_cnt; i++){
    document.getElementById('to_bookmark' + i).addEventListener('click', function(){
      var article_id = document.getElementById('invisible_tag_for_get_article_id' + i).textContent
      var path = '/users/bookmark_regist/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if(XHR.readyState == 4 && XHR.status == 200){
          document.getElementById('to_bookmark' + i).style.display = 'none'
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
}
