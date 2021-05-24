/*
このスクリプトファイルには、article_show に関する処理を記載する。
*/


var now_commented = false; /* 非同期コメントを記載したかどうか */
var now_replied = false; /* 非同期返信を記載したかどうか */
var host = window.location.host /* urlの中身 ドメイン部分*/
var loct = location.protocol + '//' /* http:// か、 https:// か */
var comment_cnt = document.getElementsByClassName('comment_text_box').length /* コメントの件数取得 */
var reply_cnt = document.getElementsByClassName('reply_show_box').length


/* コメント記入後、非同期でコメントを反映した際にでる「返信」ボタンのアクション */
document.getElementById('comment_xhr_response_a_res').addEventListener('click', function(){
  alert('このコメントに返信するには、ページをリロードしてください。')
})


/* コメントregist 非同期 */
window.addEventListener('load', function(){
  document.getElementById('comment_send_button').addEventListener('click', function(){

    var comment = document.getElementById('comment_section_written_by_user').value
    if (comment==''){
      alert('コメントが空欄です')
      exit
    }

    if (now_commented){
      alert('続けてコメントする場合は、ページをリロードしてください')
      exit
    }

    /* 非同期（is_XHR）を解除した場合このIDは存在しなくなるので、その処理 */
    if (document.getElementById('article_id_for_xhr')){
      var article_id = document.getElementById('article_id_for_xhr').value
    } else {
      exit
    }

    var path = '/users/comment_regist/'
    var url = loct + host + path + article_id

    var formDatas = document.getElementById('comment');
    var postDatas = new FormData(formDatas);
    var XHR = new XMLHttpRequest();

    XHR.open('POST', url , true);
    XHR.send(postDatas);

    XHR.onreadystatechange = function(){
      if (XHR.readyState == 4 && XHR.status == 200){
        const comments = JSON.parse(XHR.response)
        document.getElementById('comment_xhr_response_body').innerHTML = comments['comment_xhr_response_body'];
        document.getElementById('comment_xhr_response_name').innerHTML = comments['comment_xhr_response_name'];
        document.getElementById('comment_xhr_response_date').innerHTML = comments['comment_xhr_response_date'];
        document.getElementById('comment_xhr_response_img').src = comments['comment_xhr_response_img'];
        document.getElementById('comment_xhr_response_a').href = comments['comment_xhr_response_a'];
        document.getElementById('comment_xhr_response_a_del').href = comments['comment_xhr_response_a_del'];
      }

    document.getElementById('comment_xhr_response').classList.remove('asynchronous_reply_box')
    now_commented = true

    };
  }, false);
}, false);

/* コメントを非同期で削除するスクリプト  */
for (let i=1; i<comment_cnt; i++){
  if (document.getElementById('comment_asynchronous_delete' + i) != null ) {
    document.getElementById('comment_asynchronous_delete' + i).addEventListener('click', function(){

      var comment_id = document.getElementById('invisible_tag_for_get_comment_id' + i).textContent
      var path = '/users/comment_delete/'
      var url = loct + host + path + comment_id

      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          document.getElementById('comment_text_box' + i).style.display = 'none'
        }
      }
    })
  }
}

/* コメントを非同期で削除するスクリプト：非同期で表示したフォーム用 */
if (document.getElementById('comment_xhr_response_a_del_with_xhr')){
  document.getElementById('comment_xhr_response_a_del_with_xhr').addEventListener('click', function(){
    var url = document.getElementById('comment_xhr_response_a_del').href
    var XHR = new XMLHttpRequest()
    XHR.open('GET', url)
    XHR.send()

    XHR.onreadystatechange = function(){
      if (XHR.readyState == 4 && XHR.status == 200){
        document.getElementById('comment_xhr_response').style.display = 'none'
      }
    }
  })
}


/* 返信コメントを非同期で削除するスクリプト： 非同期で返信コメントが registされたとき専用 */
for (let i=1; i<comment_cnt; i++){
  if (document.getElementById('reply_xhr_response_a_del_with_xhr' + i)){
    document.getElementById('reply_xhr_response_a_del_with_xhr' + i).addEventListener('click', function(){

      var comment_id = document.getElementById('invisible_tag_for_get_comment_id' + i).textContent
      var url = document.getElementById('reply_xhr_response_a_del' + comment_id).href
      var XHR = new XMLHttpRequest()
      XHR.open('GET', url)
      XHR.send()

      XHR.onreadystatechange = function(){
        if (XHR.readyState == 4 && XHR.status == 200){
          document.getElementById('reply_xhr_response_box' + comment_id).style.display = 'none'
        }
      }
    })
  }
}


/* 返信フォームを表示させるスクリプト */
var is_open = new Array(comment_cnt)
for (let i=1; i<comment_cnt; i++){
  is_open[i] = false
  document.getElementById('open_reply_form' + i).addEventListener('click', function(){
    if (is_open[i] == false){
      document.getElementById('reply_box' + i).style.display = 'block'
      is_open[i] = true
    } else {
      document.getElementById('reply_box' + i).style.display = 'none'
      is_open[i] = false
    }
  })
}

/* 返信コメントの内容を、非同期で登録するスクリプト */
for (let i=1; i<comment_cnt; i++){
  document.getElementById('reply_asynchronous_regist_button' + i).addEventListener('click', function(){

    if (now_replied == true){
      alert ('続けて返信するには、ページをリロードしてください')
      exit
    }

    var comment_id = document.getElementById('invisible_tag_for_get_comment_id' + i).textContent
    var article_id = document.getElementById('invisible_tag_for_get_article_id').textContent
    var path = '/users/reply_regist/'
    var url = loct + host + path + comment_id + '/' + article_id

    var formDatas = document.getElementById('reply_asynchronous_form' + i);
    var postDatas = new FormData(formDatas);
    var XHR = new XMLHttpRequest();

    XHR.open('POST', url , true);
    XHR.send(postDatas);

    XHR.onreadystatechange = function(){
      if (XHR.readyState == 4 && XHR.status == 200){
        const comments = JSON.parse(XHR.response)
        document.getElementById('reply_xhr_response_body' + comment_id ).innerHTML = comments['reply_xhr_response_body']
        document.getElementById('reply_xhr_response_img' + comment_id ).src = comments['reply_xhr_response_img']
        document.getElementById('reply_xhr_response_name' + comment_id ).innerHTML = comments['reply_xhr_response_name']
        document.getElementById('reply_xhr_response_date' + comment_id ).innerHTML = comments['reply_xhr_response_date']
        document.getElementById('reply_xhr_response_a_del' + comment_id ).href = comments['reply_xhr_response_a_del']
        document.getElementById('reply_xhr_response_box' + comment_id ).style.display = 'block'
        now_replied = true
      }
    }
  })
}

/* 通常モードで表示されている返信を、非同期で削除するスクリプト */
for (let i=1; i<reply_cnt; i++){
  document.getElementById('reply_asynchronous_delete' + i).addEventListener('click', function(){

    var reply_id = document.getElementById('invisible_tag_for_get_reply_id' + i).textContent
    var article_id = document.getElementById('invisible_tag_for_get_article_id').textContent
    var path = '/users/reply_delete/'
    var url = loct + host + path + reply_id + '/' + article_id

    var XHR = new XMLHttpRequest()
    XHR.open('GET', url)
    XHR.send()

    XHR.onreadystatechange = function(){
      if (XHR.readyState == 4 && XHR.status == 200){
        document.getElementById('reply_show_box' + i).style.display = 'none'
      }
    }
  })
}


