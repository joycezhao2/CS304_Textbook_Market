// JavaScript File to add event handlers
/* global $ sendInfo progressive_enhancement_on */

// $('#dept').change(function() {
//     if (progressive_on) {
//         event.preventDefault();

//         var dept = $('#dept :selected').text();
        
//         $.post(URL,{'dept':dept},update,'json');
//     }
// })

$('select[name="departments"]').change(function() {
    var dept = $(this).val();
    $.post(URL,{'dept':dept},update);
})

function update(obj) {
    console.log(obj)
    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
    } else {
        $('#nums').empty();
        var options = obj.nums;
        console.log(options)
        for (var i=0;i<options.length;i++){
            $('<option/>').val(options[i][0]).html(options[i][0]).appendTo('#nums');
         }
        console.log(obj)
    }
}