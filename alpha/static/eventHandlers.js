// JavaScript File to add event handlers
/* global $ sendInfo progressive_enhancement_on */

$('#dept').on("click",function() {
    if (progressive_enhacement) {
        event.precentDefault();

        var dept = $(this).text();
        
        $.post(URL,{'dept':dept},update,'json');
    }
})

function update(obj) {
    console.log(obj)

    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
}}