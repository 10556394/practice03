/* ボタンを押したらコンテンツが開く、などのモーション系スクリプト */

function openClose(){
  var obj = document.getElementsByClassName('openBox');
  for (var i=0; i<obj.length; i++){
    if(obj[i].style.display == 'inline-block'){
      obj[i].style.display = 'none';
    } else {
      obj[i].style.display = 'inline-block';
    }
  }
}

