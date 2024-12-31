$(function() {
    //Change selection method in future to specify the current question(uuid)
    data_list = document.querySelectorAll("data");
    var uuid = data_list[0].value;
    var num_row_dropzone = parseInt(data_list[1].value);
    var num_index = parseInt(data_list[2].value);
    var is_multicol = "True" === data_list[3].value;

    var row = Array.from({length: num_row_dropzone}, x => null);
    var answer = {'column':null,'index':null,'rows':row};

    if(num_index === 1 & is_multicol){
        answer = {'column1':null,'column2':null,'index':null,'rows':row};
    } else if(num_index === 2){
        if(is_multicol){
            answer = {'column1':null,'column2':null,'index1':null,'index2':null,'rows':row};
        } else {
            answer = {'column':null,'index1':null,'index2':null,'rows':row};
        }
    }
    var id_answer_name = '#' + uuid + '-input';
    $(id_answer_name).val(JSON.stringify(answer));
    

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

    $(".index-set").draggable({
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

    $(".row-set").draggable({
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

    
    if(is_multicol){
        $(".drop-zone-col").droppable({
            accept: ".col-set",
            drop: function(event, ui) {
                var draggable = ui.draggable;
                var droppable = $(this);
    
                let draggable_cols = Array.from(draggable.find('.col-cell'));
                let dropzone_cols = droppable.parent().find('.drop-zone-col');
                dropzone_cols = Array.from(dropzone_cols);
    
                draggable_cols.forEach(function(ele, index){
                    dropzone_cols[index].textContent = ele.textContent;
                    $(dropzone_cols[index]).addClass('dropped-color-col');
                })
    
                var col_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['column1'] = col_num;
                $(id_answer_name).val(JSON.stringify(answer));
    
            }
        });

        $(".drop-zone-col2").droppable({
            accept: ".col-set",
            drop: function(event, ui) {
                var draggable = ui.draggable;
                var droppable = $(this);
    
                let draggable_cols = Array.from(draggable.find('.col-cell'));
                let dropzone_cols = droppable.parent().find('.drop-zone-col2');
                dropzone_cols = Array.from(dropzone_cols);
    
                draggable_cols.forEach(function(ele, index){
                    dropzone_cols[index].textContent = ele.textContent;
                    $(dropzone_cols[index]).addClass('dropped-color-col');
                })
    
                var col_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['column2'] = col_num;
                $(id_answer_name).val(JSON.stringify(answer));
    
            }
        });
    } else{

        $(".drop-zone-col").droppable({
            accept: ".col-set",
            drop: function(event, ui) {
                var draggable = ui.draggable;
                var droppable = $(this);
    
                let draggable_cols = Array.from(draggable.find('.col-cell'));
                let dropzone_cols = droppable.parent().find('.drop-zone-col');
                dropzone_cols = Array.from(dropzone_cols);
    
                draggable_cols.forEach(function(ele, index){
                    dropzone_cols[index].textContent = ele.textContent;
                    $(dropzone_cols[index]).addClass('dropped-color-col');
                })
    
                var col_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['column'] = col_num;
                $(id_answer_name).val(JSON.stringify(answer));
    
            }
        });

    }


    if(num_index === 1){
        $(".drop-zone-index").droppable({
            accept: ".index-set",
            drop: function(event, ui) {
                var draggable = ui.draggable;
                var droppable = $(this);
                
                let draggable_indice = Array.from(draggable.find('.index-cell'));
                let dropzone_indice = droppable.parent().parent().find('.drop-zone-index');
                dropzone_indice = Array.from(dropzone_indice);

                draggable_indice.forEach(function(ele, index){
                    dropzone_indice[index].textContent = ele.textContent;
                    $(dropzone_indice[index]).addClass('dropped-color-index');
                })
                
                var index_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['index'] = index_num;
                $(id_answer_name).val(JSON.stringify(answer));
            }
        });
    } else if(num_index === 2){
        $(".drop-zone-index1").droppable({
            accept: ".index-set",
            drop: function(event, ui) {
                
                var draggable = ui.draggable;
                var droppable = $(this);

                let draggable_indice = Array.from(draggable.find('.index-cell'));
                let dropzone_indice = droppable.parent().parent().find('.drop-zone-index1');
                dropzone_indice = Array.from(dropzone_indice);

                draggable_indice.forEach(function(ele, index){
                    dropzone_indice[index].textContent = ele.textContent;
                    $(dropzone_indice[index]).addClass('dropped-color-index');
                })
                
                var index_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['index1'] = index_num;
                $(id_answer_name).val(JSON.stringify(answer));
            }
        });

        $(".drop-zone-index2").droppable({
            accept: ".index-set",
            drop: function(event, ui) {
                
                var draggable = ui.draggable;
                var droppable = $(this);

                let draggable_indice = Array.from(draggable.find('.index-cell'));
                let dropzone_indice = droppable.parent().parent().find('.drop-zone-index2');
                dropzone_indice = Array.from(dropzone_indice);

                draggable_indice.forEach(function(ele, index){
                    dropzone_indice[index].textContent = ele.textContent;
                    $(dropzone_indice[index]).addClass('dropped-color-index');
                })
                
                var index_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['index2'] = index_num;
                $(id_answer_name).val(JSON.stringify(answer));
            }
        });
    } else if(num_index === 3){
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
                
                var index_num = $(ui.helper).attr('data-order');
                var id_answer_name = '#' + uuid + '-input';
                answer['index'] = index_num;
                $(id_answer_name).val(JSON.stringify(answer));
            }
        });
    }

    $(".drop-zone-row").droppable({
        accept: ".row-set",
        drop: function(event, ui) {
            var draggable = ui.draggable;
            var droppable = $(this);
            var dropzone_num = droppable.attr('order');

            let draggable_rows = Array.from(draggable.find('.row-cell'));
            let query = 'div[order="' + dropzone_num + '"]'
            let dropzone_rows = droppable.parent().parent().find(query);
            dropzone_rows = Array.from(dropzone_rows);

            draggable_rows.forEach(function(ele, index){
                dropzone_rows[index].textContent = ele.textContent;
                $(dropzone_rows[index]).addClass('dropped-color-row');
            })

            var row_num = $(ui.helper).attr('data-order');
            var id_answer_name = '#' + uuid + '-input';
            dropzone_num = parseInt(dropzone_num);
            answer['rows'][dropzone_num] = row_num;
            $(id_answer_name).val(JSON.stringify(answer));

        }
    });
    if(num_index === 1){
        if(is_multicol){
            $("#unique").click(function(){
                let cols1 = document.querySelectorAll(".drop-zone-col");
                let cols2 = document.querySelectorAll(".drop-zone-col2");
                let indice = document.querySelectorAll(".drop-zone-index");
                let rows = document.querySelectorAll(".drop-zone-row");
                console.log("sdsddssd");
                cols1.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
                cols2.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
            
                indice.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
            
                rows.forEach(ele => {
                    $(ele).removeClass('dropped-color-row');
                    ele.textContent = "\u00A0";
                })
        
                var id_answer_name = '#' + uuid + '-input';
                $(id_answer_name).val(JSON.stringify(answer));
            });

        } else{
            $("#unique").click(function(){
                let cols1 = document.querySelectorAll(".drop-zone-col");
                let indice = document.querySelectorAll(".drop-zone-index");
                let rows = document.querySelectorAll(".drop-zone-row");
                console.log("sdsddssd");
                cols1.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
            
                indice.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
            
                rows.forEach(ele => {
                    $(ele).removeClass('dropped-color-row');
                    ele.textContent = "\u00A0";
                })
        
                var id_answer_name = '#' + uuid + '-input';
                $(id_answer_name).val(JSON.stringify(answer));
            });
        }
        

    } else if(num_index === 2){
        if(is_multicol){
            $("#unique").click(function(){
                let cols1 = document.querySelectorAll(".drop-zone-col");
                let cols2 = document.querySelectorAll(".drop-zone-col2");
                let indice1 = document.querySelectorAll(".drop-zone-index1");
                let indice2 = document.querySelectorAll(".drop-zone-index2");
                let rows = document.querySelectorAll(".drop-zone-row");

                cols1.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
                cols2.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
            
                indice1.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
                indice2.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
            
                rows.forEach(ele => {
                    $(ele).removeClass('dropped-color-row');
                    ele.textContent = "\u00A0";
                })
        
                var id_answer_name = '#' + uuid + '-input';
                $(id_answer_name).val(JSON.stringify(answer));
            });

        } else {
            $("#unique").click(function(){
                let cols1 = document.querySelectorAll(".drop-zone-col");
                let indice1 = document.querySelectorAll(".drop-zone-index1");
                let indice2 = document.querySelectorAll(".drop-zone-index2");
                let rows = document.querySelectorAll(".drop-zone-row");

                cols1.forEach(ele => {
                    $(ele).removeClass('dropped-color-col');
                    ele.textContent = "Column";
                })
            
                indice1.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
                indice2.forEach(ele => {
                    $(ele).removeClass('dropped-color-index');
                    ele.textContent = "Index";
                })
            
                rows.forEach(ele => {
                    $(ele).removeClass('dropped-color-row');
                    ele.textContent = "\u00A0";
                })
        
                var id_answer_name = '#' + uuid + '-input';
                $(id_answer_name).val(JSON.stringify(answer));
            });

        }
    }
    //Change selector in future to specify button only for the current question
    

});