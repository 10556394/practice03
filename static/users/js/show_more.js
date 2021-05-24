
/* もっと見る機能 */
var show_cnt = 16 /* 表示する最小単位 */
var view_block = 1 /* 表示するブロック数 */

window.addEventListener('DOMContentLoaded', function(){
  var art_cnt = document.getElementsByClassName('art_box').length
  to_invisible(view_block, art_cnt)

  /* 表示数以上の記事は非表示にしておく */
  for (let i=show_cnt+1; i<=art_cnt * view_block; i++){
    document.getElementById('art_box' + i).style.display = 'none'
  }
  view_block += 1


  document.getElementById('show_more_button').addEventListener('click', function(){
    for (let i=show_cnt+1; i<=show_cnt*view_block; i++){
      if ( i > art_cnt ){
        break
      }
      document.getElementById('art_box' + i).style.display = 'block'
    }
    to_invisible(view_block, art_cnt)
    view_block += 1

  })
})

function to_invisible(view_block, art_cnt){
  if (show_cnt*view_block >= art_cnt){
    document.getElementById('show_more_button').style.display = 'none'
  }

}