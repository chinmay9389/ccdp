$(document).ready(function(){
    $(".modal").hide();
    $(".modal1").hide();

  $(".mybtn").click(function(){
        $(".modal").show();
  });
  
   $(".mybtn1").click(function(){
        $(".modal1").show();
  });
  
  
  $(".close").click(function(){
    $(".modal").hide();
    $(".modal1").hide();
  });
  
    $(".modal").click(function() {
       if ($(".modal").is(":visible")) {
           $(".modal").hide();
       }
    });

    $(".modal1").click(function() {
       if ($(".modal1").is(":visible")) {
           $(".modal1").hide();
       }
    });
});