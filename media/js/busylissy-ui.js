$(document).ready(function(){
    $('#notifications').fadeIn(1500).fadeTo(1500, 1).fadeOut(1000);
    
    $('a.action-delete').click(function(event) {
        event.preventDefault();
        url = $(this).attr('href');
        jConfirm('really?', 'Are you sure?', function(r) {
            if(r == true){
                location.href = url;
            }
        });
    });

    $('#js-addtask').each(function(){
        $('.insert-tag-link').click(function(event){
            event.preventDefault();
            var tag = $(this).text();
            var comma = ", ";
            
            $(this).parent().fadeOut("slow");
            var tag_string = $('#id_tags').val();
            if(tag_string.lastIndexOf(",") != (tag_string.length - 1) && tag_string.lastIndexOf(",") != (tag_string.length - 2) || ((tag_string.length > 0) && tag_string.length < 2)){
                $('#id_tags').val($('#id_tags').val() + comma);
            }
            
            $("#id_tags").val($("#id_tags").val() + tag + comma);
            
        });
    });
    
    $("#id_tags").keyup(function(){
        $('#js-addtask .insert-tag-link').each(function(){
            var tag = $(this).text();

            if($('#id_tags').val().indexOf(tag) == -1){
                $(this).parent().fadeIn("slow");
            } else {
                $(this).parent().fadeOut("slow");
            }
        });
    });

    $('#js-addtask .insert-tag-link').each(function(){
        var tag = $(this).text();

        if($('#id_tags').val().indexOf(tag) != -1){
            $(this).parent().fadeOut("slow");
        }
    });
    
    // Datepicker
    $('#id_due_date').datepicker({ dateFormat: 'yy-mm-dd' });
    $('#id_birth_date').datepicker({ dateFormat: 'yy-mm-dd' });
    $('#id_day').datepicker({ dateFormat: 'yy-mm-dd' });

    // Milestone agenda
    $('.next').click(function(event){
        event.preventDefault();
        var date = $('#calender h6:last').text().substring(4).replace("/", "-");
        var url = window.location; 

        $.get(url + 'tasks/calendar/forw/'+date, function(data){
            $('#calender').html(data).fadeIn("slow");
        });
    });

    $('.prev').click(function(event){
        event.preventDefault();
        var date = $('#calender h6:first').text().substring(4).replace("/", "-");
        var url = window.location;
        
        $.get(url + 'tasks/calendar/back/'+date, function(data){
            $('#calender').html(data).fadeIn("slow");
        });
    });

    // Add members
    $('#member a').each(function(){
        $(this).click(function(event){
            event.preventDefault();
            var comma = ", ";
            user_string = $('#id_usernames').val();
            if(user_string.lastIndexOf(",") != (user_string.length - 1) && user_string.lastIndexOf(",") != (user_string.length - 2) || ((user_string.length > 0) && user_string.length < 2)){
                $('#id_usernames').val($('#id_usernames').val() + comma);
            }
            $("#id_usernames").val($("#id_usernames").val() + $(this).find('img').attr("alt") + comma);
            $(this).parent().fadeOut("slow");
        });
    });

    $("#id_usernames").keyup(function(){
        $('#member a').each(function(){
            var member = $(this).find('img').attr("alt");

            if($('#id_usernames').val().indexOf(member) == -1){
                $(this).parent().fadeIn("slow");
            } else {
                $(this).parent().fadeOut("slow");
            }
        });
    });

    $('#member a').each(function(){
        var member = $(this).find('img').attr("alt");

        if($('#id_usernames').val().indexOf(member) != -1){
            $(this).parent().hide();
        }
    });

    // Task
    $('#toggle_tasks a.remove').click(function(ev){
        ev.preventDefault();
        $('.task-list div.done').each(function(){
                $(this).fadeOut("slow");
        });
        $(this).hide();
        $('a.show').show();
    });

    $('#toggle_tasks a.show').click(function(ev){
        ev.preventDefault();
        $('.task-list div.done').each(function(){
                $(this).fadeIn("slow");
        });
        $(this).hide();
        $('a.remove').show();
    });

    // Project Dashboard
    $('.more').click(function(ev){
        ev.preventDefault();
        $('#activity-collapse').animate({"height": "1000px"}, "1000");
        $(this).hide();
    });

    // Agenda app
    // Toggle events of members
    $('.member-calendar li a').each(function(){
        $(this).click(function(ev){
            ev.preventDefault();
            var member = $(this).next().text();
            $(this).toggleClass("unchecked");

            $('#agenda li').each(function(){
                var name = $(this).find('a').attr("name").split(" ");
                if(name[0] == member){
                    $(this).toggle();
                }
            });
        });
    });

    // Toggle event types
    $('.types-calendar li a').each(function(){
        $(this).click(function(ev){
            ev.preventDefault();
            var type = $(this).next().text().toLowerCase();
            $(this).toggleClass("unchecked");

            $('#agenda li').each(function(){
                var name = $(this).find('a').attr("name").split(" ");
                if(name[1] == type){
                    $(this).toggle();
                }
            });
        });
    });

    $('.project-calendar li a').each(function(){
        $(this).click(function(ev){
            ev.preventDefault();
            var project = $(this).attr("href");
            $(this).toggleClass("unchecked");

            $('#agenda li').each(function(){
                var name = $(this).find('a').attr("name").split(" ");
                if(name[0] == project){
                    $(this).toggle();
                }
            });
        });
    });

    // Colorize projects
    var color_arr = new Array("#e6abb8", "#e5a65c", "#95c790", "#a5b4e4", "#9fe6db", "#bababa","#cd9de4", "#d1a891", "#6ec0d0", "#e5988c", "#d0cf82", "#97e5b1", "#c896a2", "#cb9454", "#82ae7e", "#8893be", "#85c3ba", "#a4a4a4", "#b087c5", "#b38f7d", "#bd7d75", "#b0b06e", "#83c79c");
    $('.project-calendar li a').each(function(item){
        var color = color_arr[item];

        $(this).next().css({'background-color': color });
        var project = $(this).attr("href");
        $('#agenda li').each(function(){
            var name = $(this).find('a').attr("name").split(" ");
            if(name[0] == project){
                $(this).css({'background-color': color });
            }
        });
    });

    // Inscreen form
    // Common
    $('.remote').click(function(ev){
        ev.preventDefault();
        var form = $(this).attr("href") + 'remote/';
        if($('#inner-content .form').length == 0){
            $('#inner-content h2').after('<div class="form"></div>');
            $('.form').hide().load(form, function(){
                $(this).slideDown();
                $('.remote').fadeTo("slow", 0.0);
                $('#id_day').datepicker({ dateFormat: 'yy-mm-dd' });

                $('.remove-form').click(function(ev){
                    ev.preventDefault();
                    $('.remote').fadeTo("slow", 1.0);
                    $('#inner-content .form').slideUp("slow", function(){
                        $(this).remove();
                    });
                });
            });
            
        }
    });

    // Agenda
    $('.day-ordinal a').click(function(ev){
        ev.preventDefault();
        var exploded_url = $(this).attr("href").split("?");
        var form = exploded_url[0] + 'remote/?' + exploded_url[1];
        if($('#inner-content .form').length == 0){
            $('#inner-content h2').after('<div class="form"></div>');
            $('.form').hide().load(form, function(){
                $(this).slideDown();
                $('.remote').fadeTo("slow", 0.0);
                $('#id_day').datepicker({ dateFormat: 'yy-mm-dd' });

                $('.remove-form').click(function(ev){
                    ev.preventDefault();
                    $('.remote').fadeTo("slow", 1.0);
                    $('#inner-content .form').slideUp("slow", function(){
                        $(this).remove();
                    });
                });
            });
            
        } else {
            $('.form').hide().load(form).fadeIn("fast", function(){
                $('.remove-form').click(function(ev){
                    ev.preventDefault();
                    $('.remote').fadeTo("slow", 1.0);
                    $('#inner-content .form').slideUp("slow", function(){
                        $(this).remove();
                    });
                });
            });
        }

    });

    $('.event-items li a.event').click(function(ev){
        ev.preventDefault();
        var form = $(this).attr("href") + 'remote/';
        if($('#inner-content .form').length == 0){
            $('#inner-content h2').after('<div class="form"></div>');
            $('.form').hide().load(form, function(){
                $(this).slideDown();
                $('.remote').fadeTo("slow", 0.0);
                $('#id_day').datepicker({ dateFormat: 'yy-mm-dd' });

                $('.remove-form').click(function(ev){
                    ev.preventDefault();
                    $('.remote').fadeTo("slow", 1.0);
                    $('#inner-content .form').slideUp("slow", function(){
                        $(this).remove();
                    });
                });
            });
            
        } else {
            $('.form').hide().load(form).fadeIn("fast", function(){
                $('.remove-form').click(function(ev){
                    ev.preventDefault();
                    $('.remote').fadeTo("slow", 1.0);
                    $('#inner-content .form').slideUp("slow", function(){
                        $(this).remove();
                    });
                });
            });
        }

    });

    // Newsbar
    var COOKIE_NAME = 'newsbar';
    var options = { path: '/', expires: 10 };

    if(!$.cookie(COOKIE_NAME)){
        $('#top-notification').slideDown();
    }

    $('#top-notification a.close').click(function(ev){
        ev.preventDefault();
        $('#top-notification').slideUp();
        $.cookie(COOKIE_NAME, 'read', options);
    });      
});

