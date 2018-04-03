window.onload = function() {

	sliderFiller();
	sliderInit();
	writeComment();
	questionsPaginate();
	profileAlter();
	messageRead();

	$('a[href^="#"]').off().on("click", function (event) {
		event.preventDefault();
		var id  = $(this).attr('href'),
		top = $(id).offset().top;

		$('body,html').stop(true).animate({scrollTop: top}, 1000);
	});

	/*#Minimal height*/
	(function($) {
		var slides = $('.b-response__info');
		var maxH = 0;
		for(var i = 0; i < slides.length; i++) {
			if(slides.eq(i).height() > maxH) {
				maxH = slides.eq(i).height();
			}
		}

		slides.css({
			'height': maxH
		});
	})($);

	/*#Slick slider*/

	(function($) {
		$('.s-packages-content').slick({
			dots: true,
			infinite: false,
			speed: 300,
			slidesToShow: 4,
			responsive: [
			{
				breakpoint: 1041,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 2}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1,
						slidesToScroll: 1}
					}
					]
				});

		$('.b-response-wrap').slick({
			dots: true,
			speed: 300,
			slidesToScroll: 1,
			slidesToShow: 3,
			responsive: [
			{
				breakpoint: 1041,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 2
				}
			},
			{
				breakpoint: 768,
				settings: {
					slidesToShow: 1,
					slidesToScroll: 1
				}
			}
			]
		});


		$('.b-review__info').slick({
			slidesToShow: 1,
			slidesToScroll: 1,
			arrows: false,
			fade: true,
			asNavFor: '.b-review__person-wrapper'
		});

		$('.b-review__person-wrapper').slick({
			slidesToShow: 3,
			slidesToScroll: 1,
			asNavFor: '.b-review__info',
			centerMode: true,
			focusOnSelect: true,
			responsive: [
			{
				breakpoint: 1024,
				settings: {
					slidesToShow: 2,
					slidesToScroll: 1}
				},
				{
					breakpoint: 768,
					settings: {
						slidesToShow: 1,
						centerMode: false,
						slidesToScroll: 1}
					}
					]
				});

	})($);
	
	/*#Choose plan at main page*/

	$('.b-section-message__item').on('click', function(e) {
		$('.b-section-message__item').removeClass('active')
		$(this).addClass('active');
	});


	/*#Cities list*/
	
	$('.b-region-list').on('click', '.b-region-list__btn', function(e) {
		var dep_id = $(this).data('dep_id');
		fieldFiller(dep_id, "/ajax/departments_generate/" + dep_id);

		$('.b-region-list__btn').removeClass('btn-active');
		$(this).addClass('btn-active');


		var btn = $(this).parent();
		
		out:for(var i = 0; i < 7; i++) {
			$('.popup-list').append(btn.clone());

			if (btn.prop('tagName') == undefined) {
				btn = $(this).parent().prev();

				for(var j = i; j < 7; j++) {
					$('.popup-list').append(btn.clone());
					btn = btn.prev();
				}

				break out;
			} else {
				btn = btn.next();
			}
		}
		
		$('.b-region-list').animate({
			opacity: "0"
		}, 500, function(){
			$('.b-region-list').css('z-index', '-1');
			$('.popup').css('z-index', '100').animate({opacity: '1'}, 500);
		});
	});

	$('.popup-list').on('click', '.b-region-list__btn', function(e) {
		var dep_id = $(this).data('dep_id');
		fieldFiller(dep_id, "/ajax/departments_generate/" + dep_id);

		$('.b-region-list__btn').removeClass('btn-active');
		$(this).addClass('btn-active');
	});

	$('.btn-show').on('click', function() {
		$('.popup').animate({opacity: '0'}, 500, function(){
			$('.popup-list').empty();
			$('.b-region-list__btn').removeClass('btn-active');
			$('.popup').css('z-index', '-1');
			$('.b-region-list').css('z-index', '1').animate({opacity: 1}, 300);
		});
	});

	/*#Accordion*/

	$('.b-spoiler-title').on('click', function(e) {
		$('.b-spoiler-title').not($(this)).removeClass('active');
		$(this).toggleClass('active');
	});

	$('.b-btn--secondary').on('click', tabs);

	$('.b-vacancies__tab').on('click', tabs);

	$('.s-head__nav-btn').on('click', tabs);

	$('.support-btn').on('click', tabs);

	$('.message').on('click', tabs);

	/*#Pagination*/

	$('.b-blog-nav__btn').on('click', function(){
		if($(this).hasClass('active')) return;
		$('.b-blog-nav__btn').removeClass('active is-showed');
		$(this).addClass('active');
		pagination();
	});

	$('.b-blog-nav__btn-next').on('click', function() {
		var currentBtn = $('.b-blog-nav__btn.active');
		if (currentBtn.next().hasClass('b-blog-nav__btn')) {
			var nextBtn = currentBtn.next();
		} else {
			var nextBtn = $('.b-blog-nav__btn:first');
		}

		currentBtn.removeClass('active');
		nextBtn.addClass('active');

		pagination();
	});

	$('.b-blog-nav__btn-prev').on('click', function() {
		var currentBtn = $('.b-blog-nav__btn.active');

		if (currentBtn.prev().hasClass('b-blog-nav__btn')) {
			var nextBtn = currentBtn.prev();
		} else {
			var nextBtn = $('.b-blog-nav__btn:last');
		}

		currentBtn.removeClass('active');
		nextBtn.addClass('active');
		pagination();
	});

	/*#Redacting at private profile*/

	var inp = $('.profile__input input');

	$('.profile__input label').on('click', function(e) {
		inp.attr('disabled', false);
	});

	inp.focusout(function() {
		$(this).attr('disabled', true);
	});

	/*#Add files at private profile*/

	$('.profile__docs input[type=file]').on('change', function(e) {
		var reader = new FileReader();

		var targ = getTarget(e);

		for (var i = 0; i < targ.files.length; i++) {
			var file = targ.files[i];
			var img = document.createElement("img");
			var div = document.createElement('div');
			var title = document.createElement('span');
			title.classList.add('profile__doc-title');
			div.classList.add('profile__doc');
			title.innerHTML = fileName;

			var _tempArr = $(this).val().split('\\').pop().split('.');
			var fileName = _tempArr[0];

			title.innerHTML = fileName;

			var reader = new FileReader();

			reader.onloadend = function() {
				img.src = reader.result;
			}

			reader.readAsDataURL(file);
			$(this).parent().parent().before(div);
			div.append(img);
			div.append(title); 
		}
	});

	$(".file-upload input[type=file]").change(function(){
		var filename = $(this).val().replace(/.*\\/, "");
		var span = $('<span>');
		var icon = $('<i>');
		icon.addClass('far');
		icon.addClass('fa-times-circle');
		var div = $('<div>');
		div.addClass('file-upload__item');
		div.html(filename)
		$(this).parent().before(div);
		div.append(span);
		span.append(icon);

		span.on('click', function(e) {
			$(this).parent().remove();
		});
	});


	/*#Form popup at private profile*/

	$('.application-add').on('click', function(e) {
		$('.overlay').addClass('active');
		$('.overlay').children().css('opacity', '0').animate({
			opacity: 1
		}, 300);
		$('.blur').addClass('active');
	});

	$('.overlay').on('click', function(e){
		formFadeOut(e, $('.b-main-form--popup'), $('.overlay'), $('.blur'));
	});

	$('.b-main-form--popup .b-btn-primary').on('click', function(e) {
		e.preventDefault();

		$('.b-main-form--popup').fadeOut(function() {
			$('.f-form').css({
				display: 'block',
				opacity: 0
			}).animate({
				opacity: 1
			}, 300);
		});
	});

	$('.f-form #cancel').on('click',  function() {
		$('.f-form').fadeOut(function() {
			$('.b-main-form--popup').css({
				display: 'flex'
			}).animate({
				opacity: 1
			},400)
		})
	});


	/*#select options generate at questionnaire*/

	styleSelect($('.b-select--days'), 'numb' , 1, 31);
	styleSelect($('.b-select--years'), 'year' , 1920, 2000);

	$('input[name=switchCitizen]').on('click', function(e) {
		disableSelect($(this), $('#citizen'));
	});

	$('input[name=switchRegistration]').on('click', function(e) {
		disableSelect($(this), $('#selectRegistration'));
	});

	$('#the-same').on('click', function(e){
		var data = $(this).data('disable');
		var field = '[data-field=' + data + ']';
		var inputs = $(field + ' input');
		var nextField = $(field);

		if(this.checked) {
			inputs.attr('disabled', true);
			nextField.fadeOut(400); 
		} else { 
			inputs.attr('disabled', false); 
			nextField.fadeIn(400);
		}
	});

	$('input[name=switchDeal]').on('click', function() {
		var field = $('#hideDeal');

		if ($(this).val() === 'on') {
			field.fadeIn();
		} else {
			field.fadeOut();
		}
	});

	$('.questionnaire .b-btn-primary').not('[type=submit]').on('click', function(e) {
		e.preventDefault();
		var currentStep = $(this).parent();
		var nextStep = $(this).parent().next('.questionnaire__step');

		currentStep.fadeOut(400, function() {
			nextStep.fadeIn(400);
		})
	});

	/*Mobile features*/

	$('.mobile-menu').on('click', function(e) {
		$(this).toggleClass('active');
		$('.wrapper').toggleClass('active');
	});

	(function($) {
		if (document.querySelector('.s-head__nav') == null) return;
		var defaultDist = $('.s-head__nav').offset().top;
		var start = 0;
		var startTop = 0;

		$('.s-head__nav').on('touchstart', function(e) {
			start = e.changedTouches[0].clientY;
			startTop = e.changedTouches[0].pageY;
		});

		$('.s-head__nav').on('touchmove', function(e) {
			var touchobj = e.changedTouches[0];

			if (touchobj.clientY > start && startTop > defaultDist + 20) {
				e.preventDefault();
				$(this).addClass('active');
			}else if(touchobj.clientY < start && startTop > $(this).height()
				+ defaultDist - 10) {
				e.preventDefault();
				$(this).removeClass('active');
			}
		});
	})($);
	
	$('.s-head__more-btn').on('click', function(e) {
		$('.s-head__nav').toggleClass('active');
	});

	initMap();

	var header = $('header');
	var padding = header.height();

	function fixedHeader() {
		$('body').css({'padding-top': header.height()});
		header.addClass('sticky');
	};

	fixedHeader();
	$( window ).resize(fixedHeader);
}

/*#Validation*/

	$('[data-validate]').unbind().blur( function(e){
		var valType = $(this).data('validate');
		var val = $(this).val();
		var parent = this.parentElement;

		while(parent.tagName != "BODY") {
			if(parent.tagName == "FORM") {
				var form = parent;
				break;
			}else {
				parent = parent.parentElement;
			}
		}

		switch(valType)
		{
			case 'number':
			var rvNumb = /^\d+$/;
			if(val.length > 2 && val != ' ' && rvNumb.test(val))
			{
				$(this).removeClass('error').addClass('error-not');
				$(this).next('.error-box')
				.removeClass('active');
			} else {
				$(this).removeClass('error-not').addClass('error');
				$(this).next('.error-box')
				.addClass('active');
			}
			break; 
		}

		if($('[data-validate]').hasClass('error')) {
			form.classList.add('error-form');
		}else {
			form.classList.remove('error-form');
		}
	});

	$('.validateForm').on('submit', function(e) {
		e.preventDefault();
		location.href = $(this).data('link');

		if(!$(this).hasClass('error-form')) {

			$.ajax({
				url: $(this).attr('action'),
				type: 'post',
				data: $(this).serialize(),

				success: function(data){
					/*#Do something with data*/
				}
			}); 
		};
	});



function initMap() {
	if (document.getElementById('map') == null) return;
	var map = new google.maps.Map(document.getElementById('map'), {
	});
}

function disableSelect(context, select) {
	if(context.val() === 'on') {
		select.attr('disabled', false);
	} else {
		select.attr('disabled', true);
	}
}

function styleSelect(el, type, from, to) {

	if(type === 'numb') {
		for(var i = from; i <= to; i++) {
			var option = $('<option>').val(i).html(i);
			el.append(option);
		}
	}

	if(type === 'year') {
		for(var i = to; i >= from; i--) {
			var option = $('<option>').val(i).html(i);
			el.append(option);
		}
	}
}

function formFadeOut(e, form, overlay, blur) {
	if (!e.target.classList.contains('active')) return;

	overlay.children().animate({opacity: 0}, 300, function(e) {
		overlay.removeClass('active');
		blur.removeClass('active');
	});
}

function pagination() {
	var dataCount= $('.b-blog-nav__btn.active').data('blogbtn');
	var currentContent = $('.b-blog-container');
	var dataContent = $('[data-container=' + dataCount + ']');
	$('.b-blog-nav__btn').removeClass('is-showed');
	$('.b-blog-nav__btn.active').prev().addClass('is-showed');
	$('.b-blog-nav__btn.active').next().addClass('is-showed');
	currentContent.stop(true, true).animate({
		opacity: 0
	},300, function() {

		currentContent.css({display: 'none'});

		dataContent.css({
			display: 'flex',
			opacity:0
		}).animate({
			opacity: 1
		}, 300);
	});
};

function Slider(initialId, min, max) {

	if (document.querySelector(initialId) == null) return;

	var arr = initialId.split("-");
	var id = arr[2];
	var kind = arr[0];
	var sliderValue = $(kind + "-value-" + id);
	var sliderTotal = $(kind + "-total-" + id);
	var sliderHandle = $(initialId + ' .ui-slider-val');
	var quantity = sliderHandle.html().split(" ")[1];

	$(initialId).slider({
		min: min,
		max: max,
		range: "min",
		animate: "slow",
		slide: function( event, ui) {
			sliderValue.val(ui.value + ' ');
			sliderHandle.html(ui.value + ' ' + quantity);
			sliderTotal.html(ui.value + ' ' + quantity);
		},
		stop: function( event, ui) {
			var slider = $(this);
			var rate_id = slider.data('id');
			if (!rate_id) return 0;
			var term = $('#termin-total' + '-' + rate_id).html().split(' ')[0];
			var summ = $('#credit-total' + '-' + rate_id).html().split(' ')[0];
			$.ajax({
				url:'/ajax/credit_calculate/' + rate_id + '/' + term + '/' + summ,
				success: function(data){
					var res = $('#pay_spam' + rate_id);
					var value = res.html();
					res.html(data['result'] + ' ' + value.split(' ')[1]);
				}
			})
		}
	});

	sliderValue.val( $(initialId).slider("value") );

	sliderValue.change(function(){
		var value = $(this).val();
		$(initialId).slider("value", value);
		sliderHandle.html(value + ' ' + quantity);
		sliderTotal.html(value + ' ' + quantity);
	});
}

function fieldFiller (dep_id, url) {
	function textFill(data){
		$('#data-adress').html(data.address);
		$('#data-city').html(data.city);
		$('#data-localAdress').html(data.address);
		$('#data-schedule').html(data.schedule);
		$('#data-mail').html(data.email).attr('href',
			'mailto:'+ data.email);
		$('#data-phone').html(data.phone).attr('href',
			'tel:' + data.phone);
	}
	$.ajax({
		url: url,
		success: function(data) {
			for(key in data) {

					var obj = data[key];
					var officeArr = [];
//					for(var k in obj) officeArr.push(obj[k]);	

					var myLatlng = obj.lats;
					var map = new google.maps.Map(document.getElementById('map'), {
						zoom: 11,
						center: myLatlng
					});

					var iconChosen = {
		    			url: "/static/dist/img/marker-chosen.png", // url
		    			scaledSize: new google.maps.Size(25, 25), // scaled size
		    			origin: new google.maps.Point(0,0), // origin
		   				anchor: new google.maps.Point(0, 0) // anchor
		   			};

		   			var icon = {
		    			url: "/static/dist/img/marker.png", // url
		    			scaledSize: new google.maps.Size(25, 25), // scaled size
		    			origin: new google.maps.Point(0,0), // origin
		   				anchor: new google.maps.Point(0, 0) // anchor
		   			};

		   			textFill(obj);
		   			var allMarkers = [];
		   			var list_deps = []
		   			for (obj in data){
		   				list_deps.push(data[obj]);
		   			}
		   			for(var i = 0; i < list_deps.length; i++) {
		   				var marker = new google.maps.Marker({
		   					id: i,
		   					position: list_deps[i].lats,
		   					map: map,
		   					title: 'Нажмите, чтобы получить информацию по отделению'
		   				}).addListener('click', function() {
		   					textFill(list_deps[this.id]);

		   					for(var j = 0; j < allMarkers.length; j++) {
		   						allMarkers[j].f.setIcon(icon);
		   					}

		   					this.setIcon(iconChosen);
		   				});

		   				allMarkers.push(marker);
		   			}

		   			for(var j = 0; j < allMarkers.length; j++) {
		   				allMarkers[j].f.setIcon(icon);

		   				if(j == allMarkers.length - 1) allMarkers[j].f.setIcon(iconChosen);
		   			}

		   		}
		   	}
		   });

}


function sliderFiller(){
	$.ajax({
		url:'/ajax/slider_filler/',
		success: function(data){
			for(key in data){
				new Slider('#credit-slider-' + key, data[key].sum_min, data[key].sum_max);
				new Slider('#termin-slider-' + key, data[key].term_min, data[key].term_max);
			}
		}
	})
}


function writeComment(){
	$(".chat__send").on('submit', function(event){
	event.preventDefault();
    var more = $(this);
    var id_quest = more.data('id');
    var input = document.getElementById('chat__send' + id_quest).getElementsByClassName('chat__send-input')[0];
   	var container = $('#chat_body' + more.data('id'));
    $.ajax(more.attr('action'),{
        'type':'POST',
        'async':true,
        'dataType':'html',
        'data':{'content':input.value,
        		'id_quest':id_quest,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            	},
        'success':function(data,status,xhr){
        	if (data != 'fail'){
        		container_html = document.querySelector('#chat_body' + id_quest);
        		container.append(data);
        		input.value = '';
        		container_html.scrollTop = container_html.scrollHeight;
        	}
        },
        'error':function(xhr,status,error){
            //console.log(status);
        }
    });
    });
}


function questionsPaginate(){
	$(".messages__nav-btn").on('click', function(event){
    var more = $(this);
   	var container_chat = $('#chat_container');
   	var container_quest = $('#quest_container');
    $.ajax(more.data('url'),{
        'type':'GET',
        'async':true,
        'dataType':'html',
        'data':{'page':more.data('page'),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            	},
        'success':function(data,status,xhr){
        	if (data != 'fail'){
        		container_quest.html(data.split('ёёёёё')[0]);
        		container_chat.html(data.split('ёёёёё')[1]);
        		var page_btns = document.getElementsByClassName('messages__nav-btn');
        		for(var i=0; i < page_btns.length; i++){
        			page_btns[i].classList.remove('active');
        		}
        		page_btns[parseInt(more.data('page')) - 1].classList.add('active');
				$('.message').on('click', tabs);
        	}
        },
        'error':function(xhr,status,error){
            //console.log(status);
        }
    });
    });
}


function profileAlter(){
	$('.profile_data').on('change', function (event){
	var more = $(this);
	var field = more.data('field');

	if(field == 'phone'){
		var value = $('#profile-tel').val();
	}
	else if(field == 'email'){
		var value = $('#profile-mail').val();
	}
	else if(field == 'authy'){
		var value = $('#profile-checkbox').val();
	}
    $.ajax(more.attr('action'),{
        'type':'POST',
        'async':true,
        'dataType':'json',
        'data':{'field_name':field,
        		'field_value':value,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            	},
        'success':function(data,status,xhr){
        	if(data['url']){
        		window.location.replace(data['url']);
        	}
        	else{        		
        		if (data['status'] == '500'){
        			if(field == 'phone'){
        				var container = document.getElementById('help_phone');
        				container.innerHTML = data['status_message'];
        			}
        			else if(field == 'email'){
        				var container = document.getElementById('help_email');
        				container.innerHTML = data['status_message'];
        			}
        		}
        		else{
        			if(field == 'phone'){
        				var container = document.getElementById('help_phone');
        				$('#profile-tel').val(data['phone']);
        				container.innerHTML = '';
        			}
        			else if(field == 'email'){
        				var container = document.getElementById('help_email');
        				container.innerHTML = '';
        			}
        		}
        	}
        },
        'error':function(xhr,status,error){
            //console.log(status);
        }
    });
});
}


function messageRead(){
	$(".message.unreaded").on('click', function(event){
    var more = $(this);
    $.ajax(more.data('url'),{
        'type':'POST',
        'async':true,
        'dataType':'json',
        'data':{'id_quest':more.data('id'),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            	},
        'success':function(data,status,xhr){
        	if (data['status'] != '500'){
        		var numb = $('.message-numb');
        		var count = parseInt(numb.data('count')) - 1;
        		if(count == 0){
        			numb.html('');
        		}
        		else{
        			numb.html('+' + count);
        		}
        		numb.data('count', count);
        		var text = $('#chat_text' + more.data('id'));
        		var date = $('#chat_date' + more.data('id'));
        		text.css('color', '#575757');
        		date.css('color', '#575757');
        		more.removeClass('unreaded');
        		more.addClass('readed');
        	}
        },
        'error':function(xhr,status,error){
            //console.log(status);
        }
    });
    });
}



/*function wrtieQuestion(){
	$("#question_add").on('submit', function(event){
	event.preventDefault();
    var more = $(this);
    var input = $('#question_input');
    $.ajax(more.attr('action'),{
        'type':'POST',
        'async':true,
        'dataType':'json',
        'data':{'support_text':input.val(),
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            	},
        'success':function(data,status,xhr){
        	if (data['status'] != '500'){
        		var container_2 = $('.tab-content');
        		var container_1 = $('#message_new1');
        		container_1.before(data['container_1']);
        		container_2.before(data['container_2']);
        		input.val('');
        		console.log('success');
        	}
        	else{
        		console.log(0);
        	}
        },
        'error':function(xhr,status,error){
            console.log(status);
        }
    });
    });
}*/


function sliderInit(){
	var containers = $('.pay_spam');
	for(var i=0; i < containers.length; i++){
		var id = $('#' + containers[i].id).data('id');
		var term = $('#termin-total-' + id).html().split(' ')[0];
		var summ = $('#credit-total-' + id).html().split(' ')[0];
		$.ajax({
			url:'/ajax/credit_calculate/' + id + '/' + term + '/' + summ,
			async:false,
			success: function(data){
				var res = $('#pay_spam' + id);
				var value = res.html();
				res.html(data['result'] + ' ' + value.split(' ')[1]);
			}
		})
	}
}


function tabs() {
	var dataBtn = $(this).data('btn');
	var content = $('[data-content=' + dataBtn + ']');
	var currentContent = $('.tab-content');
	var clName = '.' + this.className.split(' ')[0];

	if ($(content).hasClass('is-showed')) return;

	$(clName).removeClass('active');
	$(this).addClass('active');

	currentContent.stop(true, true).animate({
		opacity: 0
	}, 300 , function() {
		currentContent.removeClass('is-showed');

		content.addClass('is-showed').animate({
			opacity: 1
		}, 300);
	});
}

function getTarget(obj) {
	var targ;
	var e=obj;
	if (e.target) targ = e.target;
	else if (e.srcElement) targ = e.srcElement;
  if (targ.nodeType == 3) // defeat Safari bug
  	targ = targ.parentNode;
  return targ;
}