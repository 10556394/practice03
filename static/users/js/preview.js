
/* 複数画像プレビュースクリプト */

$(document).on('click', '.upload-portfolio-image-btn', function() {

  var inputToUploadPortfolioImage = $(this).next('.upload-portfolio-image')
  var portfolioImageGroup = inputToUploadPortfolioImage.closest('.form-row').next('.portfolio-image-group')

  inputToUploadPortfolioImage.click()
  inputToUploadPortfolioImage.off('change').on('change', function(e) {
    if (e.target.files && e.target.files[0]) {
      var files = e.target.files
      for (var i = 0; i < files.length; i++) {
        var file = files[i]
        var reader = new FileReader()
        reader.onload = function (e) {
          portfolioImageGroup.append(`
            <div class="responsive-img" style="background-image: url(${e.target.result})"></div>
          `)
        }
        reader.readAsDataURL(file)
      }
    }
  })
});

/*　画像プレビュースクリプト１：これだと、複数画像の表示はできない　*/
document.addEventListener('DOMContentLoaded', e => {
  for (const fileInput of document.querySelectorAll('input.preview-marker')) {
    const img = document.getElementById(fileInput.dataset.target);
    const default_src = document.getElementById('for_default_preview_image').getAttribute('src');
    img.src = default_src
    if (img) {
      fileInput.addEventListener('change', e => {
        img.src = window.URL.createObjectURL(e.target.files[0]);
      });
      const initialURL = fileInput.dataset.initial;
      if (initialURL) {
        img.src = initialURL;
      }
    }
  }
});

