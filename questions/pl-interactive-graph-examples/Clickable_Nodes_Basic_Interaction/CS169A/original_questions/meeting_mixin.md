# Question 9 [3 points] Refactor a too-long method to simplify it - from S15 quiz 2

For simplicity, let’s say a meeting can be scheduled between a student and a professor if both of them are free at the desired start time.  Ben Bitdiddle proposes the following design for encapsulating the logic to determine a meeting conflict:

meeting = Meeting.new(:professor => some_prof, :student => some_student,
                      :start_time => desired_start_time)
meeting.can_be_scheduled?   # => returns true or nil/false, reports errors

Here's Ben's initial non-DRY code for can_be_scheduled?, which you will be refactoring. Note that lines 9-14 are essentially identical to 3-8 except the busy check is done on student rather than professor.

  1 class Meeting < ActiveRecord::Base
  2   def can_be_scheduled?
  3     professor_is_busy = professor.meetings.any? do |meeting|
  4       meeting.start_time == self.start_time 
  5     end
  6     if professor_is_busy
  7       self.errors.add_to_base("Professor is busy at that time")
  8     end
  9     student_is_busy = student.meetings.any? do |meeting|
 10       meeting.start_time == self.start_time
 11     end
 12     if student_is_busy
 13       self.errors.add_to_base("Student is busy at that time")
 14     end
 15     return self.errors.empty?
 16   end
 17 end




Ben would like to express the above method simply as:
class Meeting < ActiveRecord::Base
  def can_be_scheduled?
    professor.free_for_meeting?(self) && student.free_for_meeting?(self)
  end
end

Write the free_for_meeting? method that can be mixed into both Professor and Student classes to DRY out Ben’s code. Your code should preserve the behavior that the appropriate error messages get added if the meeting cannot be scheduled, that a truthy value is returned if the meeting can be scheduled, and that a non-truthy value is returned if it cannot be scheduled.  

Start from the following skeleton (reproduced on the answer sheet):

# Any solution that returns true/non-true as appropriate, and sets
# the error appropriately, is fine
module FreeForMeeting
  def free_for_meeting?(proposed)
	# Fill in your solution in Question 9
    busy = self.meetings.any? do |meeting|
      meeting.start_time == proposed.start_time
    end
    proposed.errors.add_to_base("#{self.class} busy at that time") if busy
    busy
  end
end

Technically, the original code skeleton was incorrect in using self.errors.empty? as the return value, because errors in other validations might cause this expression to be false even if the actual "is available" check succeeded. But since we gave you that code, you got full credit if you used that same test in your own solution.

Possibly helpful hint: self.class returns the class of its receiver.  You can call to_s on the result or just embed it into a string to get the printable class name.




Question 10 [2 points] multiple choice
Choose ONE. When writing the simplest possible RSpec test to test free_for_meeting?, what kind of argument should be passed to free_for_meeting?

a) Create a mock object for a meeting and stub its start_time getter, and pass the mock
b) Use a factory to create real meeting and pass that
c) Use fixtures to set up the professor, student, and various meeting objects, with the meeting times designed to span the various test cases; then pass one of the meeting fixtures

You need a real meeting object, or at least something that also implements errors.  There's no good reason to mock out errors if you can use a factory to create a real ActiveRecord object. Fixtures aren't appropriate for data that changes from test to test.
