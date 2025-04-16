# STAR Assessments course repo

## Develop your element and/or assessments

Please check out the [csxxx wiki](https://github.com/ace-lab/pl-ucb-csxxx/wiki)
for basic PrairieLearn mechanics etc.

Each study will create its own `courseInstance` in the PL repo, and
one or more `assessments` in that course instance to serve as the
study task(s).

In the examples below, substitute a
name/moniker for your course in place of `PROJECT`.  Look at the 

**Remember:** it's fine to copy boilerplate files from other
directories, but **every PL item has a unique UID (uuid)** and you
have to change those.  You can generate UUIDs with the shell command `uuidgen`.

## Develop on a branch

To avoid lots of merge collisions, it's best to do all of the below on a branch
and use that branch for local testing.  When ready, merge your branch
to the master branch.  **Please test locally first,**  because broken
content in anyone's changes can cause the whole course to fail to load
and thereby endanger others' studies.

### 1. Create and git add the directory `courseInstances/PROJECT`

In it you'll need a minimal `infoCourseInstance.json`, which you can
base on an existing one, but don't forget to change the uuid's.

### 2. Create and add `questions/PROJECT/`

This is where your question(s) will go, both those used in the study
and those used to demo your element, etc.

### 3. If you're building an element, create and add `elements/pl-*`....

...where * is whatever your element name is.

### 4. Add `courseInstances/PROJECT/assessments/infoAssessment.json`

This file specifies and sequences the PL question(s) in your study
task.  Take a look at existing ones for the relatively straightforward
syntax.  Be very careful of punctuation and closing your braces, or
the course won't load in PL.

You can setup the assessment as either a "homework" allowing unlimited
attempts per question or an "exam" that gives one chance per
question. [Here's the
documentation](https://prairielearn.readthedocs.io/en/latest/assessment/)
for configuring an assessment.

### 5. Remember you're not alone

**At this point**, all of your work should be able to go into either a
question subdirectory, the element subdirectory, or your `infoAssessment.json`.  If you find
yourself editing files other than those,
please ask us before proceeding, to avoid accidentally damaging
others' projects.

Other students/teams are editing this repo as well, so you will often
need to do a `git pull` to update your local copy of the repo before
you can successfully push changes.  If everyone respects the above
directory structure, no one's changes should cause conflicts with anyone else's.

## Sync to PrairieLearn.com

Any time the main repo changes, those changes have to be synchronized
to PrairieLearn.
Sign in to [us.prairielearn.com](PrairieLearn) using the SSO option
with CalNet (**do not use** the "sign in with Google" option even
with berkeley.edu credentials--it won't work).
The course instructors will add you as "TAs" to this course, which
gives you the ability to 
click Sync in the top navbar, then click "Pull from remote git
repository".  Make sure the sync is error-free.

Remember, you have to do this each time the master branch of the
course repo receives changes.

## Give students access to the assessment

Navigate to your course instance on PrairieLearn and you should see a list of
assessments.  Follow
 [these
 instructions](https://prairielearn.readthedocs.io/en/latest/assessment/#linking-to-assessments)
 to generate a link directly to your study's assessment.
 
 This is the link you will give to participants at the start of the
 study.  They will also have to login with CalNet when they follow the
 link; after CalNet login, they will [be automatically "enrolled" in
 your "course" and taken straight to the
 assessment](https://prairielearn.readthedocs.io/en/latest/courseInstance/#enrollment-controls),
 so don't do this until you "start the clock" for that part of the study.
 
 
