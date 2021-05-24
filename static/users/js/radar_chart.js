window.addEventListener('load', function(){

  /* ページを判断 */
  var ctx = document.getElementById("radar_chart_of_my_page")
  var cop = document.getElementById("radar_chart_of_profile")

  if ( ctx != null ){

    var power = document.getElementById('invibible_box_for_get_ability_power').textContent
    var speed = document.getElementById('invibible_box_for_get_ability_speed').textContent
    var brain = document.getElementById('invibible_box_for_get_ability_brain').textContent
    var magic = document.getElementById('invibible_box_for_get_ability_magic').textContent
    var gard = document.getElementById('invibible_box_for_get_ability_gard').textContent
    var magicgard = document.getElementById('invibible_box_for_get_ability_magicgard').textContent

    var myRadarChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Power', 'Speed', 'Brain', 'Magic', 'Gard', 'MagicGard'],
        datasets: [{
          label: '{{ username }}',
          data: [power, speed, brain, magic, gard, magicgard ],
          backgroundColor: 'rgba(197, 197, 201, 0.3)',
          borderColor: 'rgba(197, 197, 201, 0.6)',
          pointBackgroundColor: 'rgba(197, 197, 201, 0.6)',
          pointBorderColor: 'rgba(197, 197, 201, 1)',
          borderWidth: 3,
          pointRadius: 3,
      }]},
      options : {
        animation: { duration: 2000 },
        legend: { display: false },
        scale: {
          ticks: {
            min: 0,
            max: 10,
            stepSize: 2,
            backdropColor: 'rgba(197, 197, 201, 0)',
          },
          pointLabels: { fontSize: 16 },
          gridLines: {
            display: true,
            color: 'rgba(63, 63, 63, 0.5)',
          },
          angleLines: {
            display: true,
            color: 'rgba(30, 30, 30, 0.5)',
          }
        }
      }
    })
  }

  if (cop != null){

    var power = document.getElementById('invibible_box_for_get_ability_power').textContent
    var speed = document.getElementById('invibible_box_for_get_ability_speed').textContent
    var brain = document.getElementById('invibible_box_for_get_ability_brain').textContent
    var magic = document.getElementById('invibible_box_for_get_ability_magic').textContent
    var gard = document.getElementById('invibible_box_for_get_ability_gard').textContent
    var magicgard = document.getElementById('invibible_box_for_get_ability_magicgard').textContent

    var power_t = document.getElementById('invibible_box_for_get_ability_power_t').textContent
    var speed_t = document.getElementById('invibible_box_for_get_ability_speed_t').textContent
    var brain_t = document.getElementById('invibible_box_for_get_ability_brain_t').textContent
    var magic_t = document.getElementById('invibible_box_for_get_ability_magic_t').textContent
    var gard_t = document.getElementById('invibible_box_for_get_ability_gard_t').textContent
    var magicgard_t = document.getElementById('invibible_box_for_get_ability_magicgard_t').textContent

    var myRadarChart = new Chart(cop, {
      type: 'radar',
      data: {
        labels: [power_t, speed_t, brain_t, magic_t, gard_t, magicgard_t ],
        datasets: [{
          label: '{{ username }}',
          data: [power, speed, brain, magic, gard, magicgard ],
          backgroundColor: 'rgba(197, 197, 201, 0.3)',
          borderColor: 'rgba(197, 197, 201, 0.6)',
          pointBackgroundColor: 'rgba(197, 197, 201, 0.6)',
          pointBorderColor: 'rgba(197, 197, 201, 1)',
          borderWidth: 3,
          pointRadius: 3,
      }]},
      options : {
        animation: { duration: 2000 },
        legend: { display: false },
        scale: {
          ticks: {
            min: 0,
            max: 10,
            stepSize: 2,
            backdropColor: 'rgba(197, 197, 201, 0)',
          },
          pointLabels: { fontSize: 16 },
          gridLines: {
            display: true,
            color: 'rgba(63, 63, 63, 0.5)',
          },
          angleLines: {
            display: true,
            color: 'rgba(30, 30, 30, 0.5)',
          }
        }
      }
    })
  }
})