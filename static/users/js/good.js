var host = window.location.host
var loct = location.protocol + '//'

/* MEMO:
article_idの取得は、なぜか for_article_regist_asynchronous で行わないとうまく動作しない
invisible_tag_for_get_article_id では、２ページ目以降の記事が、うまく動作しなくなる

原因発見：
invisible_tag_for_get_article_id は、コメント返信フォームに記載したID。
よって、コメントが存在しない Articleには、このIDも存在しないことになる（ display:none ）。
*/


/* Memo：addEventListenerが動かないときは、window. load の記述を入れるといい */
/* Article_show のブックマーク非同期 */
window.addEventListener('load', function(){
  if(document.getElementById('link_to_bookmark_on_as_xhr') != null){
    document.getElementById('link_to_bookmark_on_as_xhr').addEventListener('click', function(){

      var article_id = document.getElementById('for_article_regist_asynchronous').textContent
      var path = '/users/bookmark_regist/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          document.getElementById('link_to_bookmark_on_as_xhr').style.display = 'none'
          document.getElementById('bookmark_button_after_click_bookmark').style.display = 'inline'
          element = document.getElementById('message_as_bookmark_complete')
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
})

/* いいね 登録 デフォルト　青ボタン */
window.addEventListener('load', function(){
  if (document.getElementById('button_to_regit_good_asynchronously') != null){
    document.getElementById('button_to_regit_good_asynchronously').addEventListener('click', function(){

      var article_id = document.getElementById('for_article_regist_asynchronous').textContent
      var path = '/users/good_regist/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          const responsed = JSON.parse(XHR.response)
          document.getElementById('display_location_as_good_count').innerHTML = responsed['good_cnt']
          document.getElementById('button_to_regit_good_asynchronously').style.display = 'none'
          document.getElementById('button_to_release_good_asynchronosuly2').firstElementChild.style.display = 'inline'
        }
      }
    })
  }
})

/* いいね 登録 非同期で処理した後の青ボタン */
window.addEventListener('load', function(){
  if (document.getElementById('button_to_regit_good_asynchronously2') != null){
    document.getElementById('button_to_regit_good_asynchronously2').addEventListener('click', function(){

      var article_id = document.getElementById('for_article_regist_asynchronous').textContent
      var path = '/users/good_regist/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          const responsed = JSON.parse(XHR.response)
          document.getElementById('display_location_as_good_count').innerHTML = responsed['good_cnt']
          document.getElementById('button_to_regit_good_asynchronously2').firstElementChild.style.display = 'none'
          document.getElementById('button_to_release_good_asynchronosuly2').firstElementChild.style.display = 'inline'
        }
      }
    })
  }
})

/* いいね 削除 デフォルト赤ボタン*/
window.addEventListener('load', function(){
  if (document.getElementById('button_to_release_good_asynchronosuly') != null){
    document.getElementById('button_to_release_good_asynchronosuly').addEventListener('click', function(){

      var article_id = document.getElementById('for_article_regist_asynchronous').textContent
      var path = '/users/good_release/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          const responsed = JSON.parse(XHR.response)
          document.getElementById('display_location_as_good_count').innerHTML = responsed['good_cnt']
          document.getElementById('button_to_release_good_asynchronosuly').style.display = 'none'
          document.getElementById('button_to_regit_good_asynchronously2').firstElementChild.style.display = 'inline'
        }
      }
    })
  }
})

/* いいね 削除 非同期後に表示する赤ボタン*/
window.addEventListener('load', function(){
  if (document.getElementById('button_to_release_good_asynchronosuly2') != null){
    document.getElementById('button_to_release_good_asynchronosuly2').addEventListener('click', function(){

      var article_id = document.getElementById('for_article_regist_asynchronous').textContent
      var path = '/users/good_release/'
      var url = loct + host + path + article_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          const responsed = JSON.parse(XHR.response)
          document.getElementById('display_location_as_good_count').innerHTML = responsed['good_cnt']
          document.getElementById('button_to_release_good_asynchronosuly2').firstElementChild.style.display = 'none'
          document.getElementById('button_to_regit_good_asynchronously2').firstElementChild.style.display = 'inline'
        }
      }
    })
  }
})