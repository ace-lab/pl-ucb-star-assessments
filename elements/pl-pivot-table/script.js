$(document).ready(function() {
    $(".col-set").draggable({
        helper: "clone",
        zIndex: 100,
        start: function (event, ui) {
            var w = $(this).css('width');
            var h = $(this).css('height');
            $(this).css({
                opacity: 0.5
            });
            ui.helper.css('width', w).css('height', h);
          },
        stop: function (event, ui) {
            var w = $(this).css('width');
            var h = $(this).css('height');
            $(this).css({
                opacity: 1
            });
            ui.helper.css('width', w).css('height', h);
          }
        
    });

    $(".index").draggable({
        helper: "clone",
        zIndex: 100,
        start: function (event, ui) {
            var w = $(this).css('width');
            var h = $(this).css('height');
            $(this).css({
                opacity: 0.5
            });
            ui.helper.css('width', w).css('height', h);
          },
        stop: function (event, ui) {
            var w = $(this).css('width');
            var h = $(this).css('height');
            $(this).css({
                opacity: 1
            });
            ui.helper.css('width', w).css('height', h);
          }
        
    });

    $(".drop-zone-col").droppable({
        accept: ".col-set",
        drop: function(event, ui) {
            var draggable = ui.draggable;
            var droppable = $(this);

            let drag_cols = Array.from(draggable.find('.col-md-2'));
            let drop_cols = Array.from(droppable.find('.col-md-2'));
            drag_cols.forEach(function(ele, index){
                drop_cols[index].textContent = ele.textContent;
                $(drop_cols[index]).addClass('dropped-color-col');
            })

        }
    });

    $(".drop-zone-index").droppable({
        accept: ".index",
        drop: function(event, ui) {
            var draggable = ui.draggable;
            var droppable = $(this);

            let drag_cols = Array.from(draggable.find('.col-md-12'));
            let drop_cols = Array.from(droppable.find('.col-md-12'));
            drag_cols.forEach(function(ele, index){
                drop_cols[index].textContent = ele.textContent;
                $(drop_cols[index]).addClass('dropped-color-index');
            })

        }
    });

    $(".drop-zone-row").droppable({
        accept: ".index",
        drop: function(event, ui) {
            var draggable = ui.draggable;
            var droppable = $(this);

            let drag_cols = Array.from(draggable.find('.col-md-12'));
            let drop_cols = Array.from(droppable.find('.col-md-12'));
            drag_cols.forEach(function(ele, index){
                drop_cols[index].textContent = ele.textContent;
                $(drop_cols[index]).addClass('dropped-color-row');
            })

        }
    });

        
    
    
});