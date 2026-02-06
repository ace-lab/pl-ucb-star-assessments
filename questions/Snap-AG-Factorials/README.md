Link to Google Slides: https://docs.google.com/presentation/d/1BwPL89MBC4caneVTdlYTDNYEt6iKgTiVnVo13djyIS8/edit?usp=sharing




1. Required Downloads:

    * If you do not already have Docker installed, you will need to install it, which you can find on the Docker website. Please note, you may experience issues with a newer Docker Desktop. In this case, you will need to downgrade to Docker Desktop version <= 4.27.2. Here are instructions to downgrade: https://stackoverflow.com/a/77224786

    * You will first need to download the the files containing the autograder, the Snap! windows embedded in PL, and the question setup. All of this can be found in the repo at the following link:https://github.com/JamesRakanathaLitanto/pl-snap.git

    * Once you have cloned the repo above, you will need to enter the folder "/pl-snap" and create a new folder titled, "pl_ag_jobs".

2. Initial Setup

    * Now you will need to configure the image and container. First, open a terminal and go to the path \pl-snap\elements\pl-snap\"Docker setup". If you have windows, you will need to open a Windows subsystem for Linxus, such as wsl. 

    * Next, input the following lines:
    `>>>> docker run -d -p <PORT>:<PORT> --name registry registry:2`

        ** Example: `>>>> docker run -d -p 5000:5000 --name registry registry:2`. Note, you will use that same port, in the lines below.

        ** If this line failed, then you are probably already using registry:2. You can either delete your current registry:2 image or rewrite the line to be registry:3, etc.

    ```
    >>>> docker pull jryl/grader-snap

    >>>> docker image tag jryl/grader-snap localhost:<PORT>/snap-test-new

    >>>> docker push localhost:<PORT>/snap-test-new

    >>>> docker build -t snap-test-new .
    ```

    * If you have an Apple Silicon instead of running `docker build -t snap-test-new .` at the end above, run the following instead: `docker build --platform linux/amd64 -t snap-test-new .`

    * Now you will need to exit out of the nested path and go the original folder "/pl-snap" and run the following line:
    ```
    >>>> docker run -it --rm -p 3000:3000 -v $PWD:/course -v "$PWD/pl_ag_jobs:/jobs" -e HOST_JOBS_DIR="$PWD/pl_ag_jobs" -v /var/run/docker.sock:/var/run/docker.sock --add-host=host.docker.internal:172.17.0.1 prairielearn/prairielearn:latest
    ```

        ** When running the docker image you may get an error like "pg_ctl: could not start server". The PrarieLearn documentation recommends the following: "To fix this, open Docker Desktop settings, click on "General", check the option to use the virtualization framework, and check "Use Rosetta for x86/amd64 emulation on Apple Silicon". Then, click "Apply & Restart"

    * You have successfully configured the setup. To open the local PL instance, open a terminal and go to: localhost:3000/pl

    * Once you have, click the "Load from disk" button and go to the "cs raka: testing for STAR" course instance. Then, click the "Questions" button to view the Snap! questions. 

3. Authoring Questions

    * If you would like to author a question, you will be working inside of the following path: "\pl-snap\questions"

    * First, create a folder in the current path. Then, enter the folder. This folder will contain four items:
        1. clientFilesQuestion
        2. tests
        3. info.json
        4. question.html
    
    * You will need to create two folders inside of "\pl-snap\questions", titled "clientFilesQuestion" and "tests". Once you have done so, you will need to enter both of these folders and create files inside of them.
    
        ** Next, enter the "clientFilesQuestion" folder. Here, you will place the starter XML file that will be displayed to the student in Snap!. The starter file should be a file that was downloaded/exported from Snap!

        ** Now, enter the "tests" folder. Here, you will place the autograder XML file that will run all tests. The autograder file should be a file that was downloaded/exported from Snap!
    
    * Now, you will need to go back to the following path: "\pl-snap\questions" and enter information for both the "info.json" and "question.html" files

        ** The info.json should have the following structure, but you will need to change the uuid and title:
            ```
                {
                "uuid": "8b4891d6-64d1-4e89-b72d-ad2133f25b2f",
                "title": "Snap! AG test",
                "topic": "Algebra",
                "tags": ["mwest", "fa17", "tpl101", "v3"],
                "type": "v3",
                "singleVariant": true,
                "gradingMethod": "External",
                    "externalGradingOptions": {
                    "enabled": true,
                    "image": "localhost:5000/snap-test-new",
                    "entrypoint": "/usr/src/cache/run_autograder",
                    "timeout": 120,
                    "enableNetworking": true
                    }
                }
            ```

        ** The question.html should have the following structure, but you will need to change both [starter-file] to the actual name of the respective file:
            ```
            <pl-question-panel>
                <p> Complete the Factorial Functions </p> 
                <p>The objective of this assessment is to complete the two functions 1. Factorial RECURSIVE and 2. Factorial ITERATIVE. You will need to write a factorial function for both blocks recursively and iteratively. You have an unlimited number of attemps.</p>
                <pl-snap source-file-name="[starter-file]"></pl-snap>
            </pl-question-panel>

            <pl-submission-panel>
                <pl-external-grader-results></pl-external-grader-results>
            </pl-submission-panel>
            ```

    * Please note that the 'pl-snap' element can take in a specific starter file, but it is NOT required. If no starter file is needed, <pl-snap></pl-snap> can be called.

    * When creating a starter file in Snap!, you will need to export the file by going to the cog icon on the right, top hand side of the screen, and then clicking "Export Project". Once you have exported the project, this file will need to be the file you place in the /pl-snap/questions/clientFilesQuestion subfolder. 

4. Examples

    * In the repo under under quesions sub-directory, there is a sample question with an autograder and starter code that tests two functions: factorial ITERATIVE and factorial RECURSIVE

    * These functions will be tested for correctness and to ensure iteration and recursion was used for the respective functions. 