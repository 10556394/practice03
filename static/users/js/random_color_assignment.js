/* インデックスページのタグ一覧用スクリプト */

window.addEventListener('load', function(){

  /* 色をランダムに割り当てる */
  var tag_cnt = document.getElementsByClassName('populer_tag').length
  for (let i=1; i<=tag_cnt; i++){
    const h = Math.random() * 240;
    document.getElementById('populer_tag_a' + i).style.backgroundColor = `hsl(${h}, 70%, 60%)`;
  }

  /* スライダー */
  /* Memo：2万行の Javascript を見て「大した事やってない」って言っていたあのプロエンジニアの言葉を思い出す。本当に javascriptって無理やりだ */
  var right_css = '<style>div.populer_tags_box:before { background: linear-gradient(to right, rgba(44,51,56,0) 0, #2c3338 80%);}</style>'
  var left_css = '<style>div.populer_tags_box:after { background: linear-gradient(to left, rgba(44,51,56,0) 0, #2c3338 80%);}</style>'

  var left_slider = document.getElementById('index_slider_left')
  var right_slider = document.getElementById('index_slider_right')
  var transparency = document.getElementById('where_to_write_style_dynamically')

  left_slider.style.display = 'none'
  transparency.innerHTML = right_css

  document.querySelectorAll('.left').forEach(elm => {
  	elm.onclick = function () {
  		let div = this.parentNode.querySelector('.populer_tags_box div');
  		div.scrollLeft -= (div.clientWidth / 2);
      left_slider.style.display = 'none'
      right_slider.style.display = 'block'
      transparency.innerHTML = right_css
  	};
  });
  document.querySelectorAll('.right').forEach(elm => {
  	elm.onclick = function () {
  		let div = this.parentNode.querySelector('.populer_tags_box div');
  		div.scrollLeft += (div.clientWidth / 2);
      left_slider.style.display = 'block'
      right_slider.style.display = 'none'
      transparency.innerHTML = left_css
  	};
  });
})


