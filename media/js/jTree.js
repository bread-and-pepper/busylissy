/* Copyright (c) 2008 Kean Loong Tan http://www.gimiti.com/kltan
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
 * Copyright notice and license must remain intact for legal use
 * jTree 1.0
 * Version: 1.0 (May 5, 2008)
 * Requires: jQuery 1.2+
 */
(function($) {

	$.fn.jTree = function(options) {
		$("body").append('<ul id="jTreeHelper"></ul>');
		var opts = $.extend({}, $.fn.jTree.defaults, options);
		var cur = 0, curOff = 0, off =0, h =0, w=0, hover = 0;
		var str='<li class="jTreePlacement" style="background:'+opts.pBg+';border:'+opts.pBorder+';color:'+opts.pColor+';height:'+opts.pHeight+'"></li>';
		var container = this;
		//events are written here
		$(this).find("li").mousedown(function(e){
			if ($("#jTreeHelper").is(":not(:animated)") && e.button !=2) {
				$("body").css("cursor","move");
				// append jTreePlacement to body and hides
				$("body").append(str);
				
				$(".jTreePlacement").hide();
				//get the current li and append to helper
				$(this).clone().appendTo("#jTreeHelper");
				
				// get initial state, cur and offset
				cur = this;
				curOff = $(cur).offset();
				$(cur).hide();
				// show initial helper
				$("#jTreeHelper").css ({
					position: "absolute",
					top: e.pageY + 5,
					left: e.pageX + 5,
					background: opts.hBg,
					opacity: opts.hOpacity
				}).hide();
				
				if(opts.showHelper)
					$("#jTreeHelper").show();
				
				$("#jTreeHelper *").css ({
					color: opts.hColor,
					background: opts.hBg
				});
				// start binding events to use
				// prevent text selection
				$(document).bind("selectstart", doNothing);
				
				// doubleclick is destructive, better disable
				$(container).find("li").bind("dblclick", doNothing);
				
				// in single li calculate the offset, width height of hovered block
				$(container).find("li").bind("mouseover", getInitial);
				
				// in single li put placement in correct places, also move the helper around
				$(container).bind("mousemove", sibOrChild);
				
				// in container put placement in correct places, also move the helper around
				$(container).find("li").bind("mousemove", putPlacement);
				
				// handle mouse movement outside our container
				$(document).bind("mousemove", helperPosition);
			}
			//prevent bubbling of mousedown
			return false;
		});
		
		// in single li or in container, snap into placement if present then destroy placement
		// and helper then show snapped in object/li
		// also destroys events
		$(this).find("li").andSelf().mouseup(function(e){
			// if placementBox is detected
			$("body").css("cursor","default");
			if ($(".jTreePlacement").is(":visible")) {
				$(cur).insertBefore(".jTreePlacement").show();
			}
			$(cur).show();
			// remove helper and placement box and clean all empty ul
			$(container).find("ul:empty").remove();
			$("#jTreeHelper").empty().hide();
			$(".jTreePlacement").remove();		
			
			// remove bindings
			destroyBindings();
			
			return false;
		});
		
		$(document).mouseup(function(e){
			$("body").css("cursor","default");
			if ($("#jTreeHelper").is(":not(:empty)")) {
				$("#jTreeHelper").animate({
					top: curOff.top,
					left: curOff.left
						}, opts.snapBack, function(){
							$("#jTreeHelper").empty().hide();
							$(".jTreePlacement").remove();
							$(cur).show();
						}
				);
				
				destroyBindings();
			}
			return false;
		});
		//functions are written here
		var doNothing = function(){
			return false;
		};
		
		var destroyBindings = function(){
			$(document).unbind("selectstart", doNothing);
			$(container).find("li").unbind("dblclick", doNothing);
			$(container).find("li").unbind("mouseover", getInitial);
			$(container).find("li").unbind("mousemove", putPlacement);
			$(document).unbind("mousemove", helperPosition);
			$(container).unbind("mousemove", sibOrChild);
			return false;
		};
		
		var helperPosition = function(e) {
			$("#jTreeHelper").css ({
				top: e.pageY + 5,
				left: e.pageX + 5
			});
			
			$(".jTreePlacement").remove();
			
			return false;
		};
		
		var getInitial = function(e){
			off = $(this).offset();
			h = $(this).height();
			w = $(this).width();
			hover = this;
			return false;
		};
		
		var sibOrChild = function(e){
			$("#jTreeHelper").css ({
				top: e.pageY + 5,
				left: e.pageX + 5
			});
			return false;
		};
		
		var putPlacement = function(e){
			$(cur).hide();
			$("#jTreeHelper").css ({
				top: e.pageY + 5,
				left: e.pageX + 5
			});
			
			
	
			//inserting before
			if ( e.pageY >= off.top && e.pageY < (off.top + h/2 - 1) ) {
				if (!$(this).prev().hasClass("jTreePlacement")) {
					$(".jTreePlacement").remove();
					$(this).before(str);
				}
			}
			//inserting after
			else if (e.pageY >(off.top + h/2) &&  e.pageY <= (off.top + h) ) {
				// as a sibling
				if (e.pageX > off.left && e.pageX < off.left + opts.childOff) {
					if (!$(this).next().hasClass("jTreePlacement")) {
						$(".jTreePlacement").remove();
						$(this).after(str);
					}
				}
				// as a child
				else if (e.pageX > off.left + opts.childOff) {
					$(".jTreePlacement").remove();
					if ($(this).find("ul").length == 0)
						$(this).append('<ul>'+str+'</ul>');
					else
						$(this).find("ul").prepend(str);
				}
			}
			
			if($(".jTreePlacement").length>1)
				$(".jTreePlacement:first-child").remove();
			return false;
		}
		
		var lockIn = function(e) {
			// if placement box is present, insert before placement box
			if ($(".jTreePlacement").length==1) {
				$(cur).insertBefore(".jTreePlacement");
			}
			$(cur).show();
			
			// remove helper and placement box
			$("#jTreeHelper").empty().hide();
			
			$(".jTreePlacement").remove();
			return false;
		}

	}; // end jTree


	$.fn.jTree.defaults = {
		showHelper: true,
		hOpacity: 0.5,
		hBg: "#FCC",
		hColor: "#222",
		pBorder: "1px dashed #CCC",
		pBg: "#EEE",
		pColor: "#222",
		pHeight: "20px",
		childOff: 20,
		snapBack: 1000
	};
		  
})(jQuery);

