$(window).ready(function(){


    // cart form

    function getOwenedProducts(id, submitSpan){
        var action = '/orders/endpoint/verify/ownership/';
        var method = 'GET';
        data = {'id' : id};
        var Owner;
        console.log('AJAX');
        $.ajax({
            url : action,
            method : method,
            data : data,
            success : function(data){
                if (data.owner){
                    Owner = true;
                    submitSpan.html('<a class="btn btn-link" href="/library/">In library</a>');
                }
                else{
                    owner = false;
                }
            },
            error : function(error){
                Owner = false;
                console.log(error);
            }
        })
    }

    var productForm = $('.addRemoveProduct');

    $.each(productForm, function(index, value){
        var $this = $(this);
        var isUser = $this.attr('data-user');
        var submitSpan = $this.find('.submit-span');
        var productInput = $this.find('[name="id"]');
        var productID = productInput.attr('value');
        var isDigital = productInput.attr('data-is-digital');
        console.log('is digital: ', isDigital);
        console.log('is user: ', isUser);
        if ( isDigital && isUser ){
            getOwenedProducts(productID, submitSpan);
        }
    });

    productForm.submit(function(event){
        event.preventDefault();
        var $this = $(this);
        var action = $this.attr('data-endpoint');
        var method = $this.attr('method');
        var data = $this.serialize();
        $.ajax({
            url : action,
            method : method,
            data : data,
            success : function(data){
                console.log('SUCCESS');
                var submitSpan = $this.find('.submit-span');
                if (data.added){
                    submitSpan.html('<button type="submit" class="btn btn-link">Remove form Cart</button>');
                }
                else{
                    submitSpan.html('<button type="submit" class="btn btn-success btn-block">Add to Cart</button>');
                }
                if (data.n > 0){
                    $('#n').text(data.n);
                }
                else{
                    $('#n').text('');
                }
                url = window.location.href
                if (url.indexOf('cart') != -1){
                    refreshCart();
                }
            },
            error : function(error){
                $.alert({
                    title: 'Opss!',
                    content: 'Something went wrong!',
                    theme : 'modern',
                });
            }
        });
    });

    function refreshCart(){
        var cartTable = $('.cart-table');
        var cartBody = $('.cart-body');
        var productRows = cartBody.find('.cart-products');
        var currentUrl = window.location.href

        console.log('Refresh Cart');
        $.ajax({
            url : '/cart/api/',
            method : 'GET',
            data : {},
            success : function(data){
                console.log('Success');
                if(data.products.length > 0){
                    productRows.html(' ');
                    var i = data.products.length;
                    var removeForm = $('#addRemoveProduct');
                    $.each(data.products, function(index, value){
                        var form = removeForm.clone();
                        form.find('.slug').attr('value', value.slug)
                        cartBody.prepend('<tr><td scope="row">' + i + '</td><td><a href="' + value.url + '">' + value.name + '</a></td><td>' + value.price + '</td><td>' + form.html() + '</td></tr>');
                        i--;
                    });
                    var total = parseFloat(data.total) + 5.99
                    cartBody.find('.cart-total').text(total);
                }
                else{
                    window.location.href = currentUrl
                }
            },
            error : function(error){
                $.alert({
                    title: 'Opss!',
                    content: 'Something went wrong!',
                    theme : 'modern',
                });
            }
        });
    }

/////////////////////////////////////////////////////////////////////////////
    // add all button
    $('.addAll').submit(function(event){
        event.preventDefault();
        console.log('ADDING');
        var form = $(this);
        var btn = form.find('[type="submit"]');
        btn.addClass('disabled');
        btn.html('<i class="fa fa-spin fa-spinner"></i>');
        var data = form.serialize();
        $.ajax({
            url : form.attr('action'),
            method : form.attr('method'),
            data : data,
            success : function(data){
                console.log('Added all');
                window.location.href = '/cart/';
            },
            error : function(error){
                $.alert({
                    title: 'Opss!',
                    content: 'Something went wrong!',
                    theme : 'modern',
                });
            }
        });
    });
    
    //////////////////////////////////////////////////////////////////////////////////////
    // search form
    var searchForm = $('.search-form');
    var input = searchForm.find('[name="q"]')
    var typingTime;
    var typingInterval = 1500;
    btn = searchForm.find('[type="submit"]');

    searchForm.keyup(function(event){
        clearTimeout(typingInterval);
        setTimeout(performSearch, typingInterval);
    });

    searchForm.keydown(function(event){
        clearTimeout(typingInterval);
    });

    function performSearch(){
        btn.addClass('disabled');
        btn.html('<i class="fa fa-spin fa-spinner"></i> Searching...');
        var q = input.val();
        setTimeout(function(){
            window.location.href = '/search/?q=' + q;
        }, 1000);
    }

    //////////////////////////////////////////////////////////////////////
    // contact form

    var contactForm = $('.contactForm');
    contactForm.submit(function(event){
        event.preventDefault();
        var form = $(this)
        form.find('[type="submit"]').addClass('disabled');
        form.find('[type="submit"]').html('<i class="fas fa-circle-notch fa-spin"></i>');
        var action = form.attr('action');
        var method = form.attr('method');
        var data = form.serialize();
        form.find('.nameErrors').text('');
        form.find('.emailErrors').text('');
        form.find('.messageErrors').text('');
        $.ajax({
            url : action,
            method : method,
            data : data,
            success : function(data){
                $.alert({
                    title: 'Thanks',
                    content: 'for sending to us',
                    theme : 'modern',
                });
                form[0].reset();
                form.find('[type="submit"]').removeClass('disabled');
                form.find('[type="submit"]').text('Send');
            },
            error : function(error){
                $.alert({
                    title: 'Opss!',
                    content: 'Something went wrong!',
                    theme : 'modern',
                });
                form.find('[type="submit"]').removeClass('disabled');
                form.find('[type="submit"]').text('Send');
                if (error.responseJSON.name){
                    form.find('.nameErrors').text(error.responseJSON.name[0].message);
                }
                if (error.responseJSON.email){
                    form.find('.emailErrors').text(error.responseJSON.email[0].message);
                }
                if (error.responseJSON.message){
                    form.find('.messageErrors').text(error.responseJSON.message[0].message);
                }
            }
        });
    });


    ////////////////////////////////////////////////////////////////////////////////
    // stripe js

    var stripe = Stripe('pk_test_VXDkskRFeTYvKtSLl5dNMmkf');

    // Create an instance of Elements.
    var elements = stripe.elements();

    // Custom styling can be passed to options when creating an Element.
    // (Note that this demo uses a wider set of styles than the guide below.)
    var style = {
    base: {
        color: '#32325d',
        lineHeight: '18px',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
        color: '#aab7c4'
        }
    },
    invalid: {
        color: '#fa755a',
        iconColor: '#fa755a'
    }
    };

    // Create an instance of the card Element.
    var card = elements.create('card', {style: style});

    // Add an instance of the card Element into the `card-element` <div>.
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
    });

    // Handle form submission.
    var form = $('#payment-form');
    form.on('submit', function(event) {
        event.preventDefault();
        var timeout;
        var errorHTML = '<i class="fa fa-warnning"></i> An error occured';
        errorClasses = 'btn btn-danger disabled my-3';
        loadingHTML = '<i class="fa fa-spinner fa-spin"></i> Loading..';
        loadingClasses = 'btn btn-success disabled my-3';
        var btn = $(this).find('button');
        stripe.createToken(card).then(function(result) {
            if (result.error) {
            // Inform the user if there was an error.
            var errorElement = $('#card-errors');
            errorElement.textContent = result.error.message;
            currentTimeout = displayBtnStatus(btn, errorHTML, errorClasses, 1000, timeout);
            } else {
            // Send the token to your server.
            stripeTokenHandler(result.token);
            currentTimeout = displayBtnStatus(btn, loadingHTML, loadingClasses, 1500, timeout);
            }
        });
    });

    function displayBtnStatus(element, newHTML, newClasses, loadTime, timeout){

        if (!loadTime){
            loadTime = 1500;
        }

        var defaultHTML = element.html();
        var defaultClasses = element.attr('class');
        element.html(newHTML);
        element.removeClass(defaultClasses);
        element.addClass(newClasses);
        return setTimeout(function(){
            element.html(defaultHTML);
            element.removeClass(newClasses);
            element.addClass(defaultClasses);
        }, loadTime);
    }

    function stripeTokenHandler(token){
        var endpoint = '/billing/create/';
        var next = $('#payment-form').find('[type="hidden"]').attr('value');
        console.log(next);
        var data = {'token' : token.id};
        $.ajax({
            url : endpoint,
            data : data,
            method : 'POST',
            success : function(data){
                console.log(data);
                card.clear();
                $.alert(data.message + '<br>Redirecting...');
                setTimeout(function(){
                    window.location.href = next;
                    console.log('redirecting')
                }, 1500);
            },
            error : function(error){
                console.log(error);
                $.alert(data.message);
            }
        });
    }
});


/////////////////////////////////////////////////////////////////////////////
// make the payment button form load when clicked

$('#payment-form').on('submit', function(event){
    
});
