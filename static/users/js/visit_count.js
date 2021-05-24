var host = window.location.host
var loct = location.protocol + '//'

window.addEventListener('load', function(){

  var article_id = document.getElementById('for_article_regist_asynchronous').textContent
  var path = '/users/visit_count/'
  var url = loct + host + path + article_id

  var XHR = new XMLHttpRequest()
  XHR.open('GET', url)
  XHR.send()

  XHR.onreadystatechange = function(){
    if (XHR.readyState == 4 && XHR.status == 200){
      const responsed = JSON.parse(XHR.response)
      document.getElementById('visit_cnt_show_box').innerHTML = responsed['visit_cnt']
    }
  }
})