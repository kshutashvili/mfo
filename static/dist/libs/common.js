window.onload = function() {

	new Slider('#credit-slider-1', 0, 15000, 500);

	new Slider('#termin-slider-1', 56, 99, 1);

	new Slider('#credit-slider-2', 0, 15000, 500);

	new Slider('#termin-slider-2', 1, 12, 1);

	new Slider('#credit-slider-3', 0, 15000, 500);

	new Slider('#termin-slider-3', 1, 12, 1);

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
		var dataCity = $(this).data('city');
		fieldFiller(dataCity, "data-city.json");
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
		var dataCity = $(this).data('city');
		fieldFiller(dataCity, "data-city.json");

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

			var _tempArr = $(this).val().split('\\').pop()
			.split('.');
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
		if(!$(this).hasClass('error-form')) {

			$.ajax({
				url: $(this).attr('action'),
				type: 'post',
				data: $(this).serialize(),

				success: function(){
					/*#Do something with data*/
				}
			}); 
		};
	});
}

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

function Slider(initialId, min, max, step) {

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
		step: step,
		slide: function( event, ui) {
			sliderValue.val(ui.value);
			sliderHandle.html(ui.value + ' ' + quantity);
			sliderTotal.html(ui.value + ' ' + quantity);
		}
	});

	sliderValue.val( $(initialId).slider("value") );

	sliderValue.change(function(){
		var value = $(this).val();
		$(initialId).slider("value", value);
		sliderHandle.html(value + ' ' + quantity);
		sliderTotal.html(value + ' ' + quantity);
	});

	/*Scroll*/
	$("a[href^='#']").off().on("click", function (event) {
		event.preventDefault();
		var id  = $(this).attr('href'),

		top = $(id).offset().top;
		
		$('body,html').stop(true).animate({scrollTop: top}, 1000);
	});


}

function fieldFiller (datacity, url) {
	function textFill(item) {
		$('#data-adress').html(item.adress);
		$('#data-city').html(item.name);
		$('#data-localAdress').html(item.localAdress);
		$('#data-schedule').html(item.schedule);
		$('#data-mail').html(item.mail).attr('href',
			'mailto:'+ item.mail);
		$('#data-phone').html(item.phone).attr('href',
			'tel:' + item.phone);
	}
	$.ajax({
		url: url,
		success: function(data) {
			for(key in data) {
				if (key === datacity) {	
					var obj = data[key];
					var officeArr = [];
					for(var k in obj) officeArr.push(obj[k]);	

						var myLatlng = officeArr[0].lats;

					var map = new google.maps.Map(document.getElementById('map'), {
						zoom: 4,
						center: myLatlng
					});

					var iconChosen = {
		    			url: "dist/img/marker-chosen.png", // url
		    			scaledSize: new google.maps.Size(25, 25), // scaled size
		    			origin: new google.maps.Point(0,0), // origin
		   				anchor: new google.maps.Point(0, 0) // anchor
		   			};

		   			var icon = {
		    			url: "dist/img/marker.png", // url
		    			scaledSize: new google.maps.Size(25, 25), // scaled size
		    			origin: new google.maps.Point(0,0), // origin
		   				anchor: new google.maps.Point(0, 0) // anchor
		   			};

		   			textFill(officeArr[0]);
		   			var allMarkers = [];

		   			for(var i = 0; i < officeArr.length; i++) {
		   				var marker = new google.maps.Marker({
		   					id: i,
		   					position: officeArr[i].lats,
		   					map: map,
		   					title: 'Нажмите, чтобы получить информацию по отделению'
		   				}).addListener('click', function() {
		   					textFill(officeArr[this.id]);

		   					for(var j = 0; j < allMarkers.length; j++) {
		   						allMarkers[j].f.setIcon(icon);
		   					}

		   					this.setIcon(iconChosen);
		   				});

		   				allMarkers.push(marker);
		   			}

		   			for(var j = 0; j < allMarkers.length; j++) {
		   				allMarkers[j].f.setIcon(icon);

		   				if(j == 0) allMarkers[j].f.setIcon(iconChosen);
		   			}
		   		}
		   	}
		   }
		 });
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