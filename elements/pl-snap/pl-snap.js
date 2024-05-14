window.setupSnapElement = (studentSubmission) => {     
        var world;

        var ide = new IDE_Morph({}),
        world = new WorldMorph(document.getElementById('world'), false);
        ide.openIn(world);        
        loop = () => {
            requestAnimationFrame(loop);
            world.doOneCycle();
        };

        if (studentSubmission != "") {
            ide.loadProjectXML(atob(studentSubmission));
        }

        world.children[0].toggleStageSize(true, .1);
        requestAnimationFrame(loop);

        updateCanvasSize = () => {
            canvas = document.getElementById('world');
            parent = document.getElementById('pl-snap');
            canvas.world = world;
            canvas.style.width = parent.offsetWidth + 'px';
            world.worldCanvas.width = parent.offsetWidth;
            world.worldCanvas.height = parseInt(canvas.style.height.slice(0, -2));
            world.setWidth(parent.offsetWidth);
            world.setHeight(world.worldCanvas.height);
            world.children.forEach(child => {
                if (child.reactToWorldResize) {
                    child.reactToWorldResize(world.bounds.copy());
                }
            });
            world.changed();
        };

        updateCanvasSize();


        window.addEventListener('resize', updateCanvasSize);
        canvas = document.getElementById('world');

        canvas.addEventListener('wheel', function(e) {
            world.hand.processMouseScroll(e);
            e.preventDefault();
        }, { passive: false });

        let buttons_primary = document.querySelectorAll('.btn-primary');
        let buttons_info = document.querySelectorAll('.btn-info');

        let button_grade, button_save;
        //find button where text is "Save & Grade", "Save", or "Save Only"
        for (let i = 0; i < buttons_primary.length; i++) {
            if (buttons_primary[i].innerText === "Save & Grade") {
                button_grade = buttons_primary[i];
            }
        }

        for (let i = 0; i < buttons_info.length; i++) {
            if (buttons_info[i].innerText === "Save") {
                button_save = buttons_info[i];
            } else if (buttons_info[i].innerText === "Save only") {
                button_save = buttons_info[i];
            }
        }

        let isSaved = false;

        button_save.addEventListener('click', (e) => {
            const canvas = document.getElementById('world');
            const ide = canvas.world.children[0];
            const submission = ide.getProjectXML();
            $("#pl-snap").find('input').val(submission);
            isSaved = true;
        });

        button_grade.addEventListener('click', (e) => {
            const canvas = document.getElementById('world')
            const ide = canvas.world.children[0];
            const submission = ide.getProjectXML();
            $("#pl-snap").find('input').val(submission);
            isSaved = true;
        });

        window.onbeforeunload = function(e) {
            if (!isSaved) {
                var dialogText = 'Document\'s changes have not been saved.';
                e.returnValue = dialogText;
                return dialogText;
            }
        };
}
