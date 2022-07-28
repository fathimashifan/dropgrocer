$(document).ready(function(){

	// $('.ratingform').submit(function(e){
	// 	var ratingd = $('.ratingnum').val()
	// 	console.log(ratingd)
	// 	if(ratingd >= 1 && ratingd <=5){
	// 		return true
	// 	}else{
	// 		alert('Enter rating number 1 to 5')
	// 		e.preventDefault()
	// 	}
	// })
	$('.promocodebtn').click(function(){
		console.log('hello')
		var promocd = $('.promocdeed').val()
		var total = $('#wishlist-total').text().replace("AED. ", "")
		// var promocd = $(this).parent().find('input').val()
		console.log(promocd)
		$.ajax({
			url: '/promocode/',
			type: 'POST',
			data: {csrfmiddlewaretoken:$('meta[name="csrf-token"]').attr('content'),'promocd':promocd},
			success:function(response){
				dis = JSON.parse(response['discountp'])
				console.log(dis['length'])
				if (dis['length'] > 0){
					$('#validdiscount').html('This promo code is applied')
					$('#promo-dis').html('<td>Promo Discount<span style="color: red;">-'+dis[0].fields.amount+'</span></td>')
					$('#notvaliddiscount').hide()
					$('#validdiscount').show()
					var disCnt = dis[0].fields.amount
					var GrandTotal = parseInt(total)-disCnt
					$('#grandtotal').html('<td>Grand Total<span>AED. '+GrandTotal+'</span></td>')
					// $('.spantable tr:nth-child(2) td:nth-child(1)').attr('rowspan',4)
				}else{
					$('#notvaliddiscount').html('This promo code you entered in invalid. Please try again.')
					$('#promo-dis').html('<td>Promo Discount<span style="color: red;">-0</span></td>')
					$('#validdiscount').hide()
					$('#notvaliddiscount').show()
					$('#grandtotal').html('<td>Grand Total<span>AED. '+total+'</span></td>')
					// $('.spantable tr:nth-child(2) td:nth-child(1)').attr('rowspan',4)
				}
			}
		})

	})

	$('#paypalRadios').click(function(){
		console.log(' hiee paypal');
		$('.orderbtn').hide()
		$('.paymentpaypal').show()
	});

	$('#codRadios').click(function(){
		console.log(' hiee cod');
		$('.paymentpaypal').hide()
		$('.orderbtn').show()
	});

	$('.searchinput').keyup(function(){
		var srch = $(this).val();
		var category = $('select[name="categoryname"]').val();
		if (srch.length > 1){
			$.ajax({
				url : 'searchlive',
				type : "POST",
				data : {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), 'search':srch, 'category': category},
				success:function(response){
					$('.searchresult').show();
					$('.searchresult').html(response.data);
				}
			})
		}else{
			$('.searchresult').hide();
		}
	})

	$('.userformsbmit').submit(function(e){
		var mobile = $('.mobilenumber').val()
		if(mobile.length == 10){
			return true
		}
		else{
			
			e.preventDefault()
		}
	});
	$('.addressedit').submit(function(e){
		var postc = $('.postcode12').val();
		console.log(postc)
		if (postc.length == 6){
			return true;
		}else{
			alert('Enter 6 digit postcode number');
			e.preventDefault();
		}
	});
	$('.checkoutform').submit(function(e){
		var postc = $('.postcode12').val();
		console.log(postc)
		if (postc.length == 6){
			return true;
		}else{
			alert('Enter 6 digit postcode number');
			e.preventDefault();
		}

	});

	$('.noteform').submit(function(e){
		e.preventDefault()
		console.log('done ha')
		notevalue = $('.notetext').val()
		console.log(notevalue)
		$('.deliverinstn').val(notevalue)
	})

	$('.addressinpt').change(function(){
		var addid = $(this).val()
		if($(this).is(':checked')){
			$('.orderconfirm').removeAttr('disabled')
			$('.selectaddress').val(addid)
			$('.addressmarg').removeClass('selectad')
			$(this).parent().parent().addClass('selectad')
		}else{
			$('.orderconfirm').attr('disabled')
		}
		
	})
	$('.checkboxinput').click(function(){
		if($(this).is(':checked')){
			// console.log('hello')
			$('.signupbtn').removeAttr('disabled')
		}else{
			$('.signupbtn').attr('disabled',true)

		}
	});

	$('.wishlistbtn').click(function(){
		var prodid = $(this).attr('data-id')
		var pname = $(this).attr('product-name')
		var prductqunatity = $('#quantity'+prodid).val()
		console.log(prodid)
		console.log(prductqunatity)
		console.log(pname)


		$('#div'+prodid).remove()
		$.ajax({
			url : 'add-to-cart',
			type : "POST",
			data : {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), 'prodid':prodid, 'pname': pname, 'quantity':prductqunatity},
			success:function(response){
				if (response["user_auth"] == false){
					$('#userLoginModal').modal('show');
				}
				else{
					var wishlist = JSON.parse(response["wishlist"]);
					var current_wishlist = JSON.parse(response["currentwishlist"]);
					var wishlisttotal = JSON.parse(response["wishlist-count"]);
					if (response["wishlist-count"] == null){
						$('#totalprice').html('AED. '+parseFloat(0).toFixed(2));
						$('#like_count').html(0);
					}else{
						$('#like_count').html(wishlist['length'])
						$('#totalprice').html('AED. '+parseFloat(wishlisttotal).toFixed(2));
						$('#quantity'+prodid).val(current_wishlist[0]['fields']['quantity'])
					}
				}
			}
		});
	});

	$('.arrowup, .wishlistbtnn12').click(function(e){
		e.preventDefault()
		var productid = $(this).attr('product-id')
		var cartnam = $(this).attr('cart-delete')
		var classn = $(this).attr('class-name')
		var plusva = $(this).parent().parent().find('input').val()
		var qiam = 0
		console.log(productid)
		console.log(cartnam)
		console.log(classn)
		console.log(plusva)


		if(cartnam){
			$('#div'+productid).remove()
		}
		if($(this).hasClass('plusarrow')){
			if(plusva>=10){
				alert('No availablity')
				e.preventDefault();
			}else{
				qiam = $(this).parent().parent().find('input').val(parseInt(plusva)+1)
				console.log(qiam.val(), 'increment')
			}
		}
	    else if (plusva>=1){
	        qiam = $(this).parent().parent().find('input').val(parseInt(plusva)-1)
	        if (qiam.val() == 0){
				$('#div'+productid).remove()}
		}
		$.ajax({
			url : 'decrement',
			type : "POST",
    		dataType: "json",
			data : {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'),'cartdele':cartnam, 'minusval' :qiam.val(), 'product_id':productid, 'classname':classn},
			success: function(response){
				if (response['is_less']){
					alert("You can't add quantity more than "+response['stock_num']+".")
				}
				if(response['wishlist'].length > 0){
					$('#quantity'+productid).val(0.00)
				}
				if(response['totalcunt'] == null){
					$('#wishlist-total').html('AED. '+parseFloat(0).toFixed(2));
					$('#like_count').html(0.00);
					$('#like_countt').html(0.00);
					$('#totalprice').html('AED. '+parseFloat(0).toFixed(2))
					$('#grandtotal').html('<td>Grand Total<span>AED. 0.00</span></td>');
					window.location.reload();
				}
				if(response['delete_wishlist'] && response['totalcunt'] && response["wishlist"] && response['dcharge']){

					var dcharge = JSON.parse(response['dcharge']);
					var wishlist = JSON.parse(response['delete_wishlist']);
					var totlacn = JSON.parse(response['totalcunt']);
					var wishlist12 = JSON.parse(response["wishlist"]);
	                var fields = wishlist12[0]["fields"];
	                var promo_dis = $('#promo-dis').find('td').find('span').text().replace('-', '');
	                total_d =dcharge+totlacn;
	                console.log('666666666666666666666666666666666666');
	                if (promo_dis != ''){
	                	grand_total = parseFloat(total_d).toFixed(2) - parseFloat(promo_dis).toFixed(2);
	                }
	                else{
	                	grand_total = parseFloat(total_d).toFixed(2);
	                }
					$('#like_count').html(wishlist['length']);
					$('#like_countt').html(wishlist['length']);
					$('#wishlist-total').html('AED. '+parseFloat(total_d).toFixed(2));
					$('#totalprice').html('AED. '+parseFloat(totlacn).toFixed(2))
					$('#price_count'+productid).html('AED. '+parseFloat(fields["total"]).toFixed(2))
					console.log('77777777777777777777777777777777777777');
					$('#quantity'+productid).val(wishlist12[0]['fields']['quantity'])
					$('#grandtotal').html('<td>Grand Total<span>AED. '+parseFloat(grand_total).toFixed(2)+'</span></td>');
				}
				else{
					if(response['error']){
						console.log('8888888888888888888888888888888888888');
						
					}else{
						var wishlist = JSON.parse(response["wishlist"]);
						var totlacn = JSON.parse(response['totalcunt']);
						$('#price_count'+productid).html('AED. '+parseFloat(0).toFixed(2))
						$('#totalprice').html('AED. '+parseFloat(0).toFixed(2))
						$('#wishlist-total').html('AED. '+parseFloat(0).toFixed(2))
						$('#like_count').html(0.00);
						$('#like_countt').html(0.00);
						$('#grandtotal').html('<td>Grand Total<span>AED. 0.00</span></td>');
					}
				}
			}
		});
	});

	$('.wishlistbt, .cartbtn, .wishlistbtndel').click(function(){
		var deletepid =$(this).attr('data-id');
		var cartpname =$(this).attr('cart-id');
		console.log(deletepid)
		console.log(cartpname)

		$('#div'+deletepid).remove()
		if(cartpname != null){
			$('#div'+deletepid).remove()
		}
		$.ajax({
			url : 'delete-wishlist',
			type : 'POST',
			data : {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), 'deletepid':deletepid, 'cartpname':cartpname},
			success:function(response){
				var wishdel = JSON.parse(response['wishlistdel']);
				var totalsum = JSON.parse(response['totalcunt']);
				var wishl = JSON.parse(response['wishlist']);
				var dcharge = JSON.parse(response['dcharge']);
				console.log(dcharge, totalsum, 'delivery')
				total_d = totalsum+dcharge
				if (totalsum == null){
					$('#wishlist-total').html('AED. '+parseFloat(0).toFixed(2))
				}
				else{
					$('#totalprice').html('AED. '+parseFloat(totalsum).toFixed(2));
					$('#like_count').html(wishdel['length'])
					$('#grandtotal').html('<td>Grand Total<span>AED. 0.00</span></td>');
				}
			}
		})

	})
	$('.heartbtn').click(function(){
		var heartpid =$(this).attr('heart-id');
		var wishlistname =$(this).attr('name');
		console.log(heartpid);
		$(this).children('i').toggleClass('heartcolor')
		$.ajax({
			url:"add_wishlist",
			
			type : 'POST',
			data : {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), 'prodid':heartpid},
			success:function(response){
				if(response['addclass'] == false){
					var element = document.getElementById("icon_"+heartpid);
  					element.classList.remove("heartcolor");
  					$('.removewishlist #snackbar').addClass('show')
					setTimeout(function(){ 
						$('.removewishlist #snackbar').removeClass('show')
						}, 3000);
				}
				else{
					var element = document.getElementById("icon_"+heartpid);
  					element.classList.add("heartcolor");
  					$('#snackbar').addClass('show')
					setTimeout(function(){ 
						$('#snackbar').removeClass('show')
						}, 3000);
				}
			}
		})
	})

	$('.rating2 a').click(function(){
		var starrate = $(this).attr('data-value')
		var productid = $(this).attr('product-id')
		$.ajax({
			url : 'star-rating',
			type : 'POST',
			data: {csrfmiddlewaretoken: $('meta[name="csrf-token"]').attr('content'), 'rating':starrate, 'productid':productid},
			success: function(response){
				var wishlist = JSON.parse(response["wishlist"]);
			}
		})
	});
	$('.marginlist #bdr0').click(function(){
		var imageval = $('#bdr0 img').attr('src')
		$('#productimage12').attr('src',imageval)
		$('.magnify-large').css("background", "url('" + imageval+ "') no-repeat")
	});
	$('.marginlist #bdr1').click(function(){
		var imageval = $('#bdr1 img').attr('src')
		$('#productimage12').attr('src',imageval)
		$('.magnify-large').css("background", "url('" + imageval+ "') no-repeat")
	});
	$('.marginlist #bdr2').click(function(){
		var imageval = $('#bdr2 img').attr('src')
		$('#productimage12').attr('src',imageval)
		$('.magnify-large').css("background", "url('" + imageval+ "') no-repeat")
	});
	$('.marginlist #bdr3').click(function(){
		var imageval = $('#bdr3 img').attr('src')
		$('#productimage12').attr('src',imageval)
		$('.magnify-large').css("background", "url('" + imageval+ "') no-repeat")
	});
	$('.marginlist #bdr4').click(function(){
		var imageval = $('#bdr4 img').attr('src')
		$('#productimage12').attr('src',imageval)
		$('.magnify-large').css("background", "url('" + imageval+ "') no-repeat")
	});


	$('.savedaddressbtn').click(function(e){
		e.preventDefault()
		$(this).prev().toggleClass('fal fas')
		$('.savedaddres').toggle()
	})
	
	var itemsMainDiv = ('.MultiCarousel');
    var itemsDiv = ('.MultiCarousel-inner');
    var itemWidth = "";

    $('.leftLst, .rightLst').click(function () {
        var condition = $(this).hasClass("leftLst");
        if (condition)
            click(0, this);
        else
            click(1, this)
    });

    ResCarouselSize();

    $(window).resize(function () {
        ResCarouselSize();
    });

    //this function define the size of the items
    function ResCarouselSize() {
        var incno = 0;
        var dataItems = ("data-items");
        var itemClass = ('.item');
        var id = 0;
        var btnParentSb = '';
        var itemsSplit = '';
        var sampwidth = $(itemsMainDiv).width();
        var bodyWidth = $('body').width();
        $(itemsDiv).each(function () {
            id = id + 1;
            var itemNumbers = $(this).find(itemClass).length;
            btnParentSb = $(this).parent().attr(dataItems);
            itemsSplit = btnParentSb.split(',');
            $(this).parent().attr("id", "MultiCarousel" + id);


            if (bodyWidth >= 1200) {
                incno = itemsSplit[3];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 992) {
                incno = itemsSplit[2];
                itemWidth = sampwidth / incno;
            }
            else if (bodyWidth >= 768) {
                incno = itemsSplit[1];
                itemWidth = sampwidth / incno;
            }
            else {
                incno = itemsSplit[0];
                itemWidth = sampwidth / incno;
            }
            $(this).css({ 'transform': 'translateX(0px)', 'width': itemWidth * itemNumbers });
            $(this).find(itemClass).each(function () {
                $(this).outerWidth(itemWidth);
            });

            $(".leftLst").addClass("over");
            $(".rightLst").removeClass("over");

        });
    }

    //this function used to move the items
    function ResCarousel(e, el, s) {
        var leftBtn = ('.leftLst');
        var rightBtn = ('.rightLst');
        var translateXval = '';
        var divStyle = $(el + ' ' + itemsDiv).css('transform');
        var values = divStyle.match(/-?[\d\.]+/g);
        var xds = Math.abs(values[4]);
        if (e == 0) {
            translateXval = parseInt(xds) - parseInt(itemWidth * s);
            $(el + ' ' + rightBtn).removeClass("over");

            if (translateXval <= itemWidth / 2) {
                translateXval = 0;
                $(el + ' ' + leftBtn).addClass("over");
            }
        }
        else if (e == 1) {
            var itemsCondition = $(el).find(itemsDiv).width() - $(el).width();
            translateXval = parseInt(xds) + parseInt(itemWidth * s);
            $(el + ' ' + leftBtn).removeClass("over");

            if (translateXval >= itemsCondition - itemWidth / 2) {
                translateXval = itemsCondition;
                $(el + ' ' + rightBtn).addClass("over");
            }
        }
        $(el + ' ' + itemsDiv).css('transform', 'translateX(' + -translateXval + 'px)');
    }

    function click(ell, ee) {
        var Parent = "#" + $(ee).parent().attr("id");
        var slide = $(Parent).attr("data-slide");
        ResCarousel(ell, Parent, slide);
    }

});
function submitform(e)
{
  console.log('form submit')
  $('#myform').submit();
  // $(thiss).addClass('')
}