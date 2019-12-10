// JavaScript File to add event handlers
/* global $ sendInfo progressive_enhancement_on */

// dynamically updates the books on the main page
$('select[name="department"]').change(function() {
    if (progressive_on) {
        event.preventDefault();
        var dept = $(this).val();
        var sort = $('#sort').val();
        $.post(URLm,{'dept':dept,'sort':sort},updatem);
    }
})

$('select[name="sorting"]').change(function() {
    if (progressive_on) {
        event.preventDefault();
        var dept = $('#dept').val();
        var sort = $(this).val();
        $.post(URLm,{'dept':dept,'sort':sort},updatem);
    }
})

// getting the list of books according to the criterias and update the books listed
function updatem(obj){
    console.log(obj)
    if(obj.error) {
        $('#errors').empty().html('Error:'+obj.err);
    } else {
        $('#book-list').empty();
        $('#book-list').append('<tr><th>Info</th><th>Action</th></tr>');
        var books = obj.books;
        console.log(books)
        for (var i=0;i<books.length;i++){
            book = books[i];
            $('#book-list').append('<tr><td class="info"><ul>'
                                    +'<li><a href="{{url_for("book",id=' + book.id + ')}}">'+book.title+'</a></li>'
                                    +'<li><lable>Price: $</label>'+book.price+'</li>'
                                    +'<li><label>Sold status: </label> Available </li>'
                                    +'</ul></td>'
                                    +'<td><form class="book" method="POST" action="/bookreq/">'
                                    +'<input type="hidden" name="bookid" value="'+book.id+'>'
                                    +'<input type="hidden" name="uid" value="'+book.seller+'>'
                                    +'<p><input type="submit" name="submit" value="Book Information"></p>'
                                    +'<p><input type="submit" name="submit" value="Seller Information"></p>'
                                    +'<p><input type="submit" name="submit" value="Add to Cart"></p>'
                                    +'</form></td></tr></table>');
        }
        console.log(obj)
    }
}

// provides existing course numbers according to the department selected on submit page
$('select[name="departments"]').change(function() {
    if (progressive_on) {
        event.preventDefault();
        var dept = $(this).val();
        $.post(URL,{'dept':dept},update);
    }
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

// dynamically changes the "mark as sold" checkbox
$("input[type=checkbox]").on('change', function() {
    bid = $(this).val();
    if (this.checked) {
        sendSoldStatus(1,bid);
    } else {
        sendSoldStatus(0,bid);
    }
});

// Send sold status and book id to the backend
function sendSoldStatus(sold_status, book_id){
    $.post(URL,{'sold_status': sold_status, 'id': book_id}, addToPage);
}

// Display the updated sold status on the page
function addToPage(json_data){
    if (json_data['sold_status'] == 0) {
        $("#sold_status").text("Available");
    }
    else {
        $("#sold_status").text("Sold");
    }
}