$('.onchange-submit').change(function(){
  $(this).closest( "form" ).trigger('submit');
});
