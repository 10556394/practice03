window.addEventListener('load', function(){

  var bar_cnt = document.getElementsByClassName('slider_line_canvas_zone').length
  var ability_max = 10
  var other_forms_cnt = 2

  for (let i=1; i<=bar_cnt; i++){

    /* メモリ線の描画ゾーンを作成 */
    var canvas = document.getElementById('canvas_zone' + (other_forms_cnt+i))
    var ctx = canvas.getContext('2d')

    var wid = canvas.width
    var hig = canvas.height

    var num_pos_y = 18
    var line_pos_y = 0

    ctx.strokeStyle = '#666';
    ctx.lineWidth = 2;

    /* メモリ線を描画 */
    for (let n=0; n<=ability_max; n++){
      x = (wid/ability_max)*n
      x = x + ((5-n)*2.4)
      y = hig

      ctx.beginPath();
      ctx.moveTo(x, line_pos_y);
      ctx.lineTo(x, y/5 );
      ctx.closePath();
      ctx.stroke();

      ctx.font = '12px';
    	ctx.fillStyle = '#cccccc';
    	ctx.textBaseline = 'center';
    	ctx.textAlign = 'center';
      ctx.fillText(n, x, num_pos_y);
    }

    /* スライダー初期値セット */
    var default_value = document.getElementById('ability_output' + (other_forms_cnt+i)).textContent
    var default_slider = document.getElementById('ability_slider' + (other_forms_cnt+i))
    if (default_value == 'None'){
      default_slider.value = 0
      document.getElementById('ability_output' + (other_forms_cnt+i)).textContent = 0
    } else {
      default_slider.value = default_value
    }

    /* スライダーを操作したときのアクション */
    var ability_slider = document.getElementById('ability_slider' + (other_forms_cnt+i))
    ability_slider.addEventListener('change', function(){
      var ability_value = this.value
      var target_name = document.getElementById('for_get_target_id' + (other_forms_cnt+i)).textContent
      document.getElementById('ability_output' + (other_forms_cnt+i)).textContent = ability_value
      document.getElementById('id_' + target_name).options[ability_value].selected = true
    })
  }
})