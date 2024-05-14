To Use the Sorting Element it will be very similar to the pl-order-blocks element as it is built into the pl-order-blocks element. 
How do we change it from pl-order-blocks is to change the grading-method attribute to "sorting". Then to create a new "subblock" for students to rearrange the elements within the inner html you can create an element that uses pl-order-sub-blocks. Then within the pl-order-sub-blocks element you list pl-answer elements to store what order the element should be in.
For example:
<pl-order-blocks answers-name="order-numbers" grading-method="sorting" partial-credit="lcs">
    <pl-order-sub-blocks>
        <pl-answer>72</pl-answer>
        <pl-answer>58</pl-answer>
    </pl-order-sub-blocks>
    <pl-order-sub-blocks>
        <pl-answer>58</pl-answer>
        <pl-answer>72</pl-answer>
    </pl-order-sub-blocks>
</pl-order-blocks>

would create two sub-blocks where the correct answer would be sorting 72, then 58 in the first sub-block and the oppisite in the next sub-block.
The order originally given to the student will be the one set in the first subblock which will be copied to the rest of the subblocks. Then for any change in the sub-block it will be copied over to all the following sub-blocks but not affecting the sub-blocks prior to it. Additionally the first sub-block is not editable as it the input. 
Other key parameters to be aware of are the answers-name parameter, this is something that can just be unique. Additionally you can change the partial-credit attribute to be "lcs" if you want to give partial credit for every placement the student gets correct. If you do not give students partial credit you can set it to "none".
The following is for in-progress slides: https://docs.google.com/presentation/d/1jKQmV2HtiGss4cjHG6cHGbdeLr1cV8Rh_xIVGWhPdjE/edit?usp=sharing  