$(document).ready(function() {
    $('#work').hide();
    $('#quality').hide();


     $('#type').change(function () {
        if ($('#type option:selected').val() == "2"){
            $('#work').show();
            
        }
         else { 
              $('#work').hide();
              $('#quality').hide();
            
         }
    });
    
    $('#work').change(function() {
        if($('#work option:selected').val() == "1") {
            $('#quality').show();
            
        }
        else {
            $('#quality').hide();
        }
    });
    
    $("#btn").click(function () {

    });
});