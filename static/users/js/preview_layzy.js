/* プロフィール編集画面の、画像プレビュースクリプト
フォームが読み込まれた後に起動したいので、記述はページ下部にしている */

const elements = $('.article_edit_photo_box').length;
var hidden_erea_start = document.getElementsByClassName('design_custom_file_input2')

/* 選択した画像をプレビューする。 */
for (let i=0; i<elements; i++){
  $(document).on('change', '#id_form-' + i + '-image', function(e) {

    var tag = document.getElementById('target_img_tag' + i);
    var file = e.target.files[0];
    var src = window.URL.createObjectURL(file);
    tag.setAttribute('src', src);

    document.getElementById('target_img_tag' + i).classList.remove('alpha30')
  });

  /* ファイルアップロード個所の不要文字を消すための処理（タグを無理やり埋め込んで、hidden処理。）
  2021.4.8
    この方法では、hiddenにできない。
    理由：埋め込んだタグが強制的に、直後で閉じられてしまうため。
    例えば、<div class="hidden">って埋め込もうとすると、強制的に<div class="hidden"></div>になるってこと
    これは、そういう仕様らしい　参考：https://language-and-engineering.hatenablog.jp/entry/20081005/1223135603
  */

  var hidden_area_end = document.getElementById('id_form-' + i + '-image')
  hidden_area_end.insertAdjacentHTML('afterend', '>');
  hidden_erea_start[i].firstElementChild.insertAdjacentHTML('afterend', '>');

}


